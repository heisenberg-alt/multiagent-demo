"""
Azure AI Foundry Agent implementation for advanced AI processing.

This module provides integration with Azure AI Foundry service for document processing
and data analysis capabilities. It supports two specialized agents:
- Document processing agent (ai_foundry_1)
- Data analysis agent (ai_foundry_2)

The agents communicate with Azure AI Foundry via REST APIs using Azure AD authentication
for secure access to AI services.

Example:
    ```python
    from agents.ai_foundry_agent import AIFoundryAgent
    from utils.config import Config
    
    config = Config()
    agent = AIFoundryAgent(
        config=config,
        agent_id="ai_foundry_1",
        specialization="document_processing"
    )
    
    await agent.initialize()
    response = await agent.query(request, user_context)
    ```

Note:
    This agent includes fallback mock responses for testing when Azure AI Foundry
    endpoints are not available.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import aiohttp
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from models.agent_models import AgentResponse, AgentCapability, AgentType
from models.chat_models import ChatMessage, ChatSession
from utils.config import Config
from utils.logger import setup_logger
from utils.telemetry import telemetry_client

logger = setup_logger(__name__)

class AIFoundryAgent:
    """
    Azure AI Foundry agent implementation for advanced AI processing.
    
    This class provides integration with Azure AI Foundry service for document processing
    and data analysis tasks. Each agent can be specialized for different use cases.
    
    Attributes:
        config (Config): Application configuration
        agent_id (str): Unique identifier for this agent instance
        specialization (str): Agent specialization type
        credential: Azure authentication credential
        ai_foundry_endpoint (str): Azure AI Foundry API endpoint
        subscription_id (str): Azure subscription ID
        resource_group (str): Azure resource group name
        ai_foundry_resource (str): Azure AI Foundry resource name
        mock_mode (bool): Whether agent is running in mock mode
        session: HTTP session for API calls
        access_token (str): Current access token
        token_expires_at (datetime): Token expiration time
        
    Supported Specializations:
        - "document_processing": Document extraction and analysis
        - "data_analysis": Data processing and statistical analysis
    """
    
    def __init__(self, config: Config, agent_id: str = "ai_foundry_1", specialization: str = "general"):
        self.config = config
        self.agent_id = agent_id
        self.specialization = specialization
        self.credential = DefaultAzureCredential()
        self.ai_foundry_endpoint = config.get_setting("AZURE_AI_FOUNDRY_ENDPOINT")
        self.subscription_id = config.get_setting("AZURE_SUBSCRIPTION_ID")
        self.resource_group = config.get_setting("AZURE_RESOURCE_GROUP")
        self.ai_foundry_resource = config.get_setting("AZURE_AI_FOUNDRY_RESOURCE")
        
        # Mock mode for development/testing
        self.mock_mode = not all([
            self.ai_foundry_endpoint,
            self.subscription_id,
            self.resource_group,
            self.ai_foundry_resource
        ])
        
        if self.mock_mode:
            logger.warning(f"AI Foundry agent {self.agent_id} ({self.specialization}) running in mock mode - some configuration missing")
        
        # Initialize session
        self.session = None
        self.access_token = None
        self.token_expires_at = None
        
    async def initialize(self) -> bool:
        """Initialize the AI Foundry agent."""
        try:
            if self.mock_mode:
                logger.info(f"AI Foundry agent {self.agent_id} ({self.specialization}) initialized in mock mode")
                return True
                
            # Get access token
            token_response = await self._get_access_token()
            if not token_response:
                logger.error("Failed to get access token for AI Foundry")
                return False
                
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'MultiagentDemo/1.0'
                }
            )
            
            # Verify connection
            if await self._verify_connection():
                logger.info(f"AI Foundry agent {self.agent_id} ({self.specialization}) initialized successfully")
                telemetry_client.track_event("ai_foundry_agent_initialized", properties={"agent_id": self.agent_id, "specialization": self.specialization})
                return True
            else:
                logger.error(f"Failed to verify AI Foundry connection for agent {self.agent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize AI Foundry agent: {e}")
            telemetry_client.track_exception(e)
            return False
    
    async def _get_access_token(self) -> bool:
        """Get access token for AI Foundry API."""
        try:
            # Use Azure Identity to get token
            token = self.credential.get_token("https://management.azure.com/.default")
            self.access_token = token.token
            self.token_expires_at = datetime.fromtimestamp(token.expires_on)
            return True
            
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return False
    
    async def _verify_connection(self) -> bool:
        """Verify connection to AI Foundry service."""
        try:
            if self.mock_mode:
                return True
                
            # Try to list available agents
            url = f"{self.ai_foundry_endpoint}/agents"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return True
                else:
                    logger.warning(f"AI Foundry connection check failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"AI Foundry connection verification failed: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get capabilities of the AI Foundry agent."""
        try:
            if self.mock_mode:
                return self._get_specialized_capabilities()
            
            # Get real capabilities from AI Foundry
            url = f"{self.ai_foundry_endpoint}/agents/capabilities"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        AgentCapability(
                            name=cap.get("name", "unknown"),
                            description=cap.get("description", ""),
                            parameters=cap.get("parameters", [])
                        )
                        for cap in data.get("capabilities", [])
                    ]
                else:
                    logger.warning(f"Failed to get AI Foundry capabilities: {response.status}")
                    return self._get_specialized_capabilities()
                    
        except Exception as e:
            logger.error(f"Failed to get AI Foundry capabilities: {e}")
            return self._get_specialized_capabilities()
    
    def _get_specialized_capabilities(self) -> List[AgentCapability]:
        """Get specialized capabilities based on agent specialization."""
        if self.specialization == "data_analytics":
            return [
                AgentCapability(
                    name="data_analysis",
                    description="Advanced data analysis and statistical modeling",
                    input_types=["csv", "json", "xlsx"],
                    output_types=["json", "report"],
                    parameters={"data_source": "str", "analysis_type": "str", "model_parameters": "dict"}
                ),
                AgentCapability(
                    name="predictive_modeling",
                    description="Create predictive models using machine learning",
                    input_types=["csv", "json"],
                    output_types=["model", "predictions"],
                    parameters={"training_data": "str", "model_type": "str", "target_variable": "str"}
                ),
                AgentCapability(
                    name="data_visualization",
                    description="Create interactive data visualizations and dashboards",
                    input_types=["csv", "json"],
                    output_types=["chart", "dashboard"],
                    parameters={"data_source": "str", "chart_type": "str", "visualization_config": "dict"}
                ),
                AgentCapability(
                    name="statistical_analysis",
                    description="Perform statistical analysis and hypothesis testing",
                    input_types=["csv", "json"],
                    output_types=["statistics", "report"],
                    parameters={"dataset": "str", "statistical_tests": "list", "confidence_level": "float"}
                )
            ]
        elif self.specialization == "document_processing":
            return [
                AgentCapability(
                    name="document_extraction",
                    description="Extract structured data from unstructured documents",
                    input_types=["pdf", "docx", "txt"],
                    output_types=["json", "csv"],
                    parameters={"document_url": "str", "extraction_schema": "dict", "output_format": "str"}
                ),
                AgentCapability(
                    name="text_classification",
                    description="Classify documents into categories",
                    input_types=["txt", "pdf", "docx"],
                    output_types=["classification"],
                    parameters={"document_content": "str", "classification_model": "str", "categories": "list"}
                ),
                AgentCapability(
                    name="content_summarization",
                    description="Generate summaries of long documents",
                    input_types=["txt", "pdf", "docx"],
                    output_types=["summary"],
                    parameters={"document_content": "str", "summary_length": "int", "key_points": "list"}
                ),
                AgentCapability(
                    name="document_comparison",
                    description="Compare documents for similarity and differences",
                    input_types=["txt", "pdf", "docx"],
                    output_types=["comparison_report"],
                    parameters={"document1": "str", "document2": "str", "comparison_criteria": "list"}
                )
            ]
        else:  # general
            return [
                AgentCapability(
                    name="document_analysis",
                    description="Analyze and extract information from documents",
                    input_types=["pdf", "docx", "txt"],
                    output_types=["analysis_report"],
                    parameters={"document_url": "str", "analysis_type": "str"}
                ),
                AgentCapability(
                    name="data_processing",
                    description="Process and transform data using workflows",
                    input_types=["csv", "json"],
                    output_types=["processed_data"],
                    parameters={"data_source": "str", "transformation_rules": "dict"}
                ),
                AgentCapability(
                    name="workflow_automation",
                    description="Automate business processes with visual workflows",
                    input_types=["workflow_definition"],
                    output_types=["workflow_result"],
                    parameters={"workflow_definition": "dict", "trigger_conditions": "list"}
                ),
                AgentCapability(
                    name="cognitive_services",
                    description="Leverage Azure Cognitive Services capabilities",
                    input_types=["text", "image", "audio"],
                    output_types=["analysis_result"],
                    parameters={"service_type": "str", "input_data": "any", "configuration": "dict"}
                )
            ]
    
    async def process_request(self, request_data: Dict[str, Any], session: Optional[ChatSession] = None) -> AgentResponse:
        """Process a request using AI Foundry agent."""
        start_time = datetime.now()
        
        try:
            if self.mock_mode:
                return await self._mock_process_request(request_data, session)
            
            # Prepare request payload
            payload = {
                "agent_type": "ai_foundry",
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "request": request_data,
                "session_id": session.session_id if session else None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send request to AI Foundry
            url = f"{self.ai_foundry_endpoint}/agents/process"
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process response
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    # Determine agent type based on agent_id
                    agent_type = AgentType.AI_FOUNDRY_1 if self.agent_id == "ai_foundry_1" else AgentType.AI_FOUNDRY_2
                    
                    agent_response = AgentResponse(
                        success=True,
                        response=str(data.get("response", {})),
                        agent_type=agent_type,
                        agent_id=self.agent_id,
                        confidence=data.get("confidence", 0.8),
                        execution_time=processing_time,
                        metadata={
                            "agent_id": self.agent_id,
                            "specialization": self.specialization,
                            "workflow_id": data.get("workflow_id"),
                            "processing_steps": data.get("processing_steps", []),
                            "resources_used": data.get("resources_used", [])
                        }
                    )
                    
                    telemetry_client.track_event(
                        "ai_foundry_request_processed",
                        properties={
                            "processing_time": processing_time,
                            "confidence_score": agent_response.confidence_score,
                            "session_id": session.session_id if session else "none"
                        }
                    )
                    
                    return agent_response
                    
                else:
                    logger.error(f"AI Foundry request failed: {response.status}")
                    agent_type = AgentType.AI_FOUNDRY_1 if self.agent_id == "ai_foundry_1" else AgentType.AI_FOUNDRY_2
                    return AgentResponse(
                        success=False,
                        response=f"Request failed with status {response.status}",
                        agent_type=agent_type,
                        agent_id=self.agent_id,
                        confidence=0.0,
                        execution_time=(datetime.now() - start_time).total_seconds(),
                        error=f"Request failed with status {response.status}",
                        metadata={"error": True, "agent_id": self.agent_id, "specialization": self.specialization}
                    )
                    
        except Exception as e:
            logger.error(f"AI Foundry request processing failed: {e}")
            telemetry_client.track_exception(e)
            
            agent_type = AgentType.AI_FOUNDRY_1 if self.agent_id == "ai_foundry_1" else AgentType.AI_FOUNDRY_2
            return AgentResponse(
                success=False,
                response=f"Processing failed: {str(e)}",
                agent_type=agent_type,
                agent_id=self.agent_id,
                confidence=0.0,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
                metadata={"error": True, "exception": str(e), "agent_id": self.agent_id, "specialization": self.specialization}
            )
    
    async def _mock_process_request(self, request_data: Dict[str, Any], session: Optional[ChatSession] = None) -> AgentResponse:
        """Mock implementation for development/testing."""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Generate mock response based on specialization and request
        mock_responses = {}
        
        if self.specialization == "data_analytics":
            mock_responses = {
                "data_analysis": {
                    "analysis_result": "Statistical analysis completed on 10,000 records",
                    "statistical_measures": {"mean": 45.2, "std": 12.8, "p_value": 0.03},
                    "insights": ["Strong correlation found", "Seasonal patterns detected"],
                    "confidence": 0.94
                },
                "predictive_modeling": {
                    "model_type": "Random Forest",
                    "accuracy": 0.87,
                    "feature_importance": {"feature_1": 0.45, "feature_2": 0.32, "feature_3": 0.23},
                    "predictions": "Generated 500 predictions with 87% accuracy",
                    "confidence": 0.91
                }
            }
        elif self.specialization == "document_processing":
            mock_responses = {
                "document_extraction": {
                    "extracted_entities": ["Company: ACME Corp", "Date: 2024-01-15", "Amount: $50,000"],
                    "document_type": "Invoice",
                    "pages_processed": 3,
                    "confidence": 0.96
                },
                "text_classification": {
                    "category": "Financial Document",
                    "subcategory": "Invoice",
                    "confidence_score": 0.89,
                    "classification_model": "BERT-based classifier",
                    "confidence": 0.89
                }
            }
        else:  # general
            mock_responses = {
                "document_analysis": {
                    "analysis_result": "Document contains 5 pages with financial data",
                    "extracted_entities": ["Company Name", "Revenue", "Profit"],
                    "confidence": 0.92
                },
                "data_processing": {
                    "processed_records": 1500,
                    "transformation_applied": "Data normalized and cleaned",
                    "output_format": "JSON",
                    "confidence": 0.88
                }
            }
        
        # Determine response type
        capability = request_data.get("capability", list(mock_responses.keys())[0] if mock_responses else "general")
        response_data = mock_responses.get(capability, {"result": "Processing completed", "confidence": 0.85})
        
        agent_type = AgentType.AI_FOUNDRY_1 if self.agent_id == "ai_foundry_1" else AgentType.AI_FOUNDRY_2
        
        return AgentResponse(
            success=True,
            response=str(response_data),
            agent_type=agent_type,
            agent_id=self.agent_id,
            confidence=response_data.get("confidence", 0.85),
            execution_time=0.5,
            metadata={
                "mock_mode": True,
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "capability": capability,
                "session_id": session.session_id if session else None
            }
        )
    
    async def chat(self, message: str, session: ChatSession) -> str:
        """Handle chat interaction with AI Foundry agent."""
        try:
            if self.mock_mode:
                return await self._mock_chat(message, session)
            
            # Prepare chat request
            payload = {
                "message": message,
                "session_id": session.session_id,
                "agent_id": self.agent_id,
                "specialization": self.specialization,
                "conversation_history": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in session.messages[-10:]  # Last 10 messages for context
                ],
                "agent_type": "ai_foundry"
            }
            
            # Send chat request
            url = f"{self.ai_foundry_endpoint}/agents/chat"
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "I couldn't process your request.")
                else:
                    logger.error(f"AI Foundry chat failed: {response.status}")
                    return "I'm having trouble connecting to the AI Foundry service right now."
                    
        except Exception as e:
            logger.error(f"AI Foundry chat failed: {e}")
            return "I encountered an error while processing your request."
    
    async def _mock_chat(self, message: str, session: ChatSession) -> str:
        """Mock chat implementation."""
        # Simulate processing time
        await asyncio.sleep(0.3)
        
        # Generate contextual responses based on specialization
        message_lower = message.lower()
        
        if self.specialization == "data_analytics":
            if "data" in message_lower or "analysis" in message_lower:
                return f"I'm {self.agent_id}, specialized in data analytics. I can help you with statistical analysis, predictive modeling, and data visualization. What type of data analysis do you need?"
            elif "model" in message_lower or "predict" in message_lower:
                return "I can create predictive models using machine learning algorithms. What kind of prediction are you looking to make?"
            elif "hello" in message_lower or "hi" in message_lower:
                return f"Hello! I'm {self.agent_id}, your data analytics specialist. I can help with statistical analysis, predictive modeling, and data visualization."
            else:
                return f"As a data analytics specialist, I can help you analyze patterns, create predictive models, and visualize your data. What specific analytics task can I assist you with?"
        
        elif self.specialization == "document_processing":
            if "document" in message_lower or "text" in message_lower:
                return f"I'm {self.agent_id}, specialized in document processing. I can extract data, classify documents, and summarize content. What documents do you need help with?"
            elif "extract" in message_lower:
                return "I can extract structured data from various document types. What information do you need to extract?"
            elif "hello" in message_lower or "hi" in message_lower:
                return f"Hello! I'm {self.agent_id}, your document processing specialist. I can handle document extraction, classification, and summarization."
            else:
                return f"As a document processing specialist, I can extract data, classify documents, and generate summaries. What document processing task can I help you with?"
        
        else:  # general
            if "document" in message_lower:
                return f"I'm {self.agent_id}, a general AI Foundry agent. I can help you analyze documents using AI workflows. What type of document analysis do you need?"
            elif "data" in message_lower:
                return "I can process and transform your data using visual workflows. What kind of data processing are you looking for?"
            elif "workflow" in message_lower:
                return "I can help you create automated workflows using AI Foundry's visual designer. What business process would you like to automate?"
            elif "hello" in message_lower or "hi" in message_lower:
                return f"Hello! I'm {self.agent_id}, an AI Foundry agent. I can help you with document analysis, data processing, and workflow automation."
            else:
                return f"I understand you're asking about '{message}'. I can help you create solutions for various business needs. What specific task would you like to accomplish?"
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the AI Foundry agent."""
        agent_type = AgentType.AI_FOUNDRY_1 if self.agent_id == "ai_foundry_1" else AgentType.AI_FOUNDRY_2
        
        return {
            "name": f"AI Foundry Agent {self.agent_id}",
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "type": agent_type.value,
            "description": f"AI Foundry agent specialized in {self.specialization}",
            "capabilities": [cap.dict() for cap in await self.get_capabilities()],
            "status": "active" if not self.mock_mode else "mock",
            "version": "1.0.0",
            "supported_formats": ["json", "xml", "csv", "pdf", "docx"],
            "max_file_size": "50MB",
            "processing_modes": ["batch", "streaming", "real-time"]
        }
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
                
            logger.info(f"AI Foundry agent {self.agent_id} ({self.specialization}) cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during AI Foundry agent {self.agent_id} cleanup: {e}")
    
    async def query(self, request: 'AgentRequest', user_context: 'UserContext') -> 'AgentResponse':
        """
        Query the AI Foundry agent with a user request.
        
        This method provides a consistent interface for querying the agent,
        converting AgentRequest to the internal request format.
        
        Args:
            request (AgentRequest): User request containing query, context, and parameters
            user_context (UserContext): User authentication and context information
            
        Returns:
            AgentResponse: Structured response from the AI Foundry agent
        """
        # Convert AgentRequest to internal format
        request_data = {
            "query": request.query,
            "context": request.context,
            "parameters": request.parameters,
            "capability": self._determine_capability_from_query(request.query),
            "user_context": {
                "user_id": user_context.user_id,
                "username": user_context.username,
                "email": user_context.email,
                "tenant_id": user_context.tenant_id
            }
        }
        
        # Use existing process_request method
        return await self.process_request(request_data)
    
    def _determine_capability_from_query(self, query: str) -> str:
        """
        Determine the appropriate capability based on the query content.
        
        Args:
            query (str): User query text
            
        Returns:
            str: Capability name to use for processing
        """
        query_lower = query.lower()
        
        if self.specialization == "document_processing":
            if any(keyword in query_lower for keyword in ["extract", "document", "text", "pdf", "contract"]):
                return "document_extraction"
            elif any(keyword in query_lower for keyword in ["classify", "category", "type"]):
                return "text_classification"
            elif any(keyword in query_lower for keyword in ["summarize", "summary", "overview"]):
                return "content_summarization"
            elif any(keyword in query_lower for keyword in ["compare", "similarity", "difference"]):
                return "document_comparison"
            else:
                return "document_extraction"  # default
                
        elif self.specialization == "data_analysis":
            if any(keyword in query_lower for keyword in ["analyze", "analysis", "data", "trends"]):
                return "data_analysis"
            elif any(keyword in query_lower for keyword in ["predict", "forecast", "model"]):
                return "predictive_modeling"
            elif any(keyword in query_lower for keyword in ["visualize", "chart", "graph", "plot"]):
                return "data_visualization"
            elif any(keyword in query_lower for keyword in ["statistics", "statistical", "hypothesis"]):
                return "statistical_analysis"
            else:
                return "data_analysis"  # default
                
        else:
            return "general_processing"
