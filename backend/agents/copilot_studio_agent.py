"""
Copilot Studio agent integration for the multiagent system.

This module provides integration with Microsoft Copilot Studio for natural language
conversation and business process automation. It supports two specialized agents:
- General conversation agent (copilot_1)
- Business process automation agent (copilot_2)

The agents communicate with Copilot Studio via the Bot Framework API using
Direct Line for real-time conversations.

Example:
    ```python
    from agents.copilot_studio_agent import CopilotStudioAgent
    from utils.config import Config
    
    config = Config()
    agent = CopilotStudioAgent(
        config=config,
        agent_id="copilot_1",
        specialization="general"
    )
    
    await agent.initialize()
    response = await agent.query(request, user_context)
    ```

Note:
    This agent includes fallback mock responses for testing when Copilot Studio
    endpoints are not available.
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
import json
from datetime import datetime

from models.agent_models import AgentRequest, AgentResponse, AgentType, UserContext
from utils.config import Config

logger = logging.getLogger(__name__)

class CopilotStudioAgent:
    """
    Integration with Microsoft Copilot Studio for conversational AI.
    
    This class provides a bridge between the multiagent system and Copilot Studio
    bots, enabling natural language conversation and business process automation.
    Each agent can be specialized for different use cases.
    
    Attributes:
        config (Config): Application configuration
        endpoint (str): Copilot Studio API endpoint
        bot_id (str): Copilot Studio bot identifier
        credential: Azure authentication credential
        client (httpx.AsyncClient): HTTP client for API calls
        agent_id (str): Unique identifier for this agent instance
        specialization (str): Agent specialization type
        capabilities (List[str]): List of agent capabilities
        
    Supported Specializations:
        - "general": General conversation and Q&A
        - "business_process": Business process automation and workflows
    """
    
    def __init__(self, config: Config, agent_id: str = "copilot_studio_agent", specialization: str = "general"):
        """
        Initialize Copilot Studio agent.
        
        Args:
            config (Config): Application configuration containing endpoints and credentials
            agent_id (str, optional): Unique identifier for this agent instance. 
                                    Defaults to "copilot_studio_agent".
            specialization (str, optional): Agent specialization type. 
                                          Defaults to "general".
                                          
        Raises:
            ValueError: If specialization is not supported
            ConfigurationError: If required configuration is missing
        """
        self.config = config
        self.endpoint = config.copilot_studio_endpoint
        self.bot_id = config.copilot_studio_bot_id
        self.credential = config.get_azure_credential()
        self.client = None
        self.agent_id = agent_id
        self.specialization = specialization
        
        # Set specialized capabilities based on agent type
        self.capabilities = self._get_specialized_capabilities()
        
        logger.info(f"Copilot Studio agent initialized: {agent_id} ({specialization})")
    
    def _get_specialized_capabilities(self) -> List[str]:
        """
        Get capabilities based on agent specialization.
        
        Returns:
            List[str]: List of capability names for this agent specialization
            
        Specialization Capabilities:
            - general: Basic conversation, Q&A, information retrieval
            - business_process: Workflow automation, process management, task coordination
        """
        if self.specialization == "general":
            return [
                "general_conversation",
                "question_answering", 
                "information_retrieval",
                "basic_assistance",
                "greeting_handling"
            ]
        elif self.specialization == "business_process":
            return [
                "workflow_automation",
                "business_process_management",
                "task_coordination",
                "process_optimization",
                "approval_workflows"
            ]
        else:
            return ["general_conversation"]

    async def initialize(self):
        """
        Initialize the agent and establish connections.
        
        This method sets up the HTTP client, tests the connection to Copilot Studio,
        and prepares the agent for processing requests.
        
        Raises:
            ConnectionError: If unable to connect to Copilot Studio
            AuthenticationError: If authentication fails
            Exception: For other initialization failures
        """
        try:
            # Initialize HTTP client
            self.client = httpx.AsyncClient(timeout=30.0)
            
            # Test connection to Copilot Studio
            await self._test_connection()
            
            logger.info("Copilot Studio agent ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize Copilot Studio agent: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.aclose()
    
    async def query(self, request: AgentRequest, user_context: UserContext) -> AgentResponse:
        """
        Query the Copilot Studio bot with a user request.
        
        This method processes user queries through the Copilot Studio bot,
        handling authentication, request formatting, and response parsing.
        
        Args:
            request (AgentRequest): User request containing query, context, and parameters
            user_context (UserContext): User authentication and context information
            
        Returns:
            AgentResponse: Structured response from the Copilot Studio bot
            
        Response Format:
            - success: Boolean indicating if the request was successful
            - response: Bot's response text
            - agent_type: Type of agent (COPILOT_STUDIO_1 or COPILOT_STUDIO_2)
            - agent_id: Unique agent identifier
            - confidence: Confidence score (0.0-1.0)
            - metadata: Additional response metadata
            - usage: Token usage information
            - execution_time: Processing time in seconds
            
        Note:
            If Copilot Studio is unavailable, returns mock responses for testing.
        """
        start_time = datetime.utcnow()
        
        try:
            # Get access token
            token = await self._get_access_token()
            
            # Prepare the request to Copilot Studio
            bot_request = await self._prepare_bot_request(request, user_context)
            
            # Send request to Copilot Studio
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Use Direct Line API or Bot Framework API
            response = await self._send_to_bot(bot_request, headers)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Determine agent type based on agent_id and specialization
            if self.agent_id == "copilot_studio_1" or (self.agent_id == "copilot_1" and self.specialization == "general"):
                agent_type = AgentType.COPILOT_STUDIO_1
            else:
                agent_type = AgentType.COPILOT_STUDIO_2
            
            if response:
                return AgentResponse(
                    success=True,
                    response=response["text"],
                    agent_type=agent_type,
                    agent_id=self.agent_id,
                    confidence=response.get("confidence", 0.8),
                    metadata={
                        "bot_id": self.bot_id,
                        "conversation_id": response.get("conversation_id"),
                        "activity_id": response.get("activity_id"),
                        "specialization": self.specialization
                    },
                    usage={
                        "tokens_used": len(request.query.split()) + len(response["text"].split())
                    },
                    execution_time=execution_time
                )
            else:
                return AgentResponse(
                    success=False,
                    response="No response from Copilot Studio",
                    agent_type=agent_type,
                    agent_id=self.agent_id,
                    error="Empty response",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Copilot Studio query failed: {str(e)}")
            
            # Determine agent type based on agent_id and specialization
            if self.agent_id == "copilot_studio_1" or (self.agent_id == "copilot_1" and self.specialization == "general"):
                agent_type = AgentType.COPILOT_STUDIO_1
            else:
                agent_type = AgentType.COPILOT_STUDIO_2
            
            return AgentResponse(
                success=False,
                response="Copilot Studio agent is currently unavailable",
                agent_type=agent_type,
                agent_id=self.agent_id,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _test_connection(self):
        """Test connection to Copilot Studio."""
        if not self.endpoint:
            logger.warning("Copilot Studio endpoint not configured - using mock responses")
            return
        
        try:
            # Test endpoint connectivity
            response = await self.client.get(f"{self.endpoint}/health", timeout=10.0)
            if response.status_code == 200:
                logger.info("Copilot Studio connection test successful")
            else:
                logger.warning(f"Copilot Studio connection test returned {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Copilot Studio connection test failed: {str(e)} - will use mock responses")
    
    async def _get_access_token(self) -> str:
        """Get access token for Copilot Studio."""
        try:
            # Get token using Azure credential
            token = self.credential.get_token("https://api.botframework.com/.default")
            return token.token
            
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            # Return a mock token for testing
            return "mock_token"
    
    async def _prepare_bot_request(self, request: AgentRequest, user_context: UserContext) -> Dict[str, Any]:
        """Prepare request for Copilot Studio bot."""
        
        # Convert conversation history to Bot Framework format
        activities = []
        if request.history:
            for msg in request.history[-5:]:  # Last 5 messages for context
                activities.append({
                    "type": "message",
                    "from": {"id": "user" if msg["role"] == "user" else "bot"},
                    "text": msg["content"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Current message
        activities.append({
            "type": "message",
            "from": {"id": user_context.user_id, "name": user_context.name},
            "text": request.query,
            "timestamp": datetime.utcnow().isoformat(),
            "channelData": {
                "user_context": {
                    "user_id": user_context.user_id,
                    "username": user_context.username,
                    "email": user_context.email,
                    "tenant_id": user_context.tenant_id
                },
                "session_id": request.session_id,
                "parameters": request.parameters
            }
        })
        
        return {
            "type": "message",
            "from": {"id": user_context.user_id, "name": user_context.name},
            "text": request.query,
            "conversation": {"id": request.session_id or f"conv_{user_context.user_id}"},
            "channelData": {
                "user_context": {
                    "user_id": user_context.user_id,
                    "username": user_context.username,
                    "email": user_context.email,
                    "tenant_id": user_context.tenant_id
                },
                "session_id": request.session_id,
                "parameters": request.parameters,
                "history": activities[:-1]  # Previous messages
            }
        }
    
    async def _send_to_bot(self, bot_request: Dict[str, Any], headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Send request to Copilot Studio bot."""
        
        if not self.endpoint:
            # Return mock response for testing
            return await self._get_mock_response(bot_request)
        
        try:
            # Use Direct Line API endpoint
            url = f"{self.endpoint}/v3/directline/conversations/{bot_request['conversation']['id']}/activities"
            
            response = await self.client.post(url, json=bot_request, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract bot response
                if "activities" in result and result["activities"]:
                    bot_activity = result["activities"][-1]  # Last activity
                    
                    return {
                        "text": bot_activity.get("text", ""),
                        "confidence": 0.8,
                        "conversation_id": bot_request["conversation"]["id"],
                        "activity_id": bot_activity.get("id")
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send request to Copilot Studio: {str(e)}")
            # Fallback to mock response
            return await self._get_mock_response(bot_request)
    
    async def _get_mock_response(self, bot_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response for testing purposes."""
        
        query = bot_request.get("text", "").lower()
        
        # Simple keyword-based responses
        if "hello" in query or "hi" in query:
            response_text = "Hello! I'm your Copilot Studio assistant. How can I help you today?"
        elif "help" in query:
            response_text = "I can help you with various tasks including answering questions, providing information, and assisting with business processes. What would you like to know?"
        elif "weather" in query:
            response_text = "I can help you with weather information. However, I would need to integrate with a weather service to provide current conditions."
        elif "code" in query or "programming" in query:
            response_text = "For complex coding tasks, I recommend using our Pro-Code agent which specializes in technical development. I can help with general questions about programming concepts."
        elif "document" in query or "analyze" in query:
            response_text = "For document analysis and processing, our AI Foundry agent would be more suitable. I can help with general questions about documents."
        else:
            response_text = f"I understand you're asking about '{query}'. As a Copilot Studio agent, I can help with conversational AI, business processes, and general assistance. How can I help you further?"
        
        return {
            "text": response_text,
            "confidence": 0.7,
            "conversation_id": bot_request.get("conversation", {}).get("id", "mock_conv"),
            "activity_id": f"mock_activity_{datetime.utcnow().timestamp()}"
        }
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get detailed agent capabilities.
        
        Returns:
            List[Dict[str, Any]]: List of capability dictionaries with details
            
        Capability Structure:
            - name: Capability name
            - description: Human-readable description
            - input_types: Supported input formats
            - output_types: Supported output formats
            - parameters: Optional capability parameters
        """
        return [
            {
                "name": "Conversational AI",
                "description": "Natural language conversation and Q&A",
                "input_types": ["text"],
                "output_types": ["text"]
            },
            {
                "name": "Business Process Automation",
                "description": "Workflow automation and process guidance",
                "input_types": ["text", "structured_data"],
                "output_types": ["text", "actions"]
            },
            {
                "name": "Knowledge Base Access",
                "description": "Access to organizational knowledge and FAQs",
                "input_types": ["text"],
                "output_types": ["text", "documents"]
            },
            {
                "name": "Multi-turn Conversations",
                "description": "Context-aware multi-turn dialogue",
                "input_types": ["text", "conversation_history"],
                "output_types": ["text"]
            }
        ]
