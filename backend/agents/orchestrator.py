"""
LangChain-based orchestrator for coordinating multiple AI agents.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import asyncio
from datetime import datetime
import uuid

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.schema.runnable import Runnable
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import AzureChatOpenAI

from models.agent_models import (
    AgentRequest, AgentResponse, OrchestrationRequest, OrchestrationResponse,
    AgentType, UserContext, AgentConfiguration, AgentMetrics
)
from models.chat_models import ChatMessage, ChatSession, ChatResponse, MessageRole
from agents.copilot_studio_agent import CopilotStudioAgent
from agents.ai_foundry_agent import AIFoundryAgent
from utils.config import Config
from utils.telemetry import TelemetryManager

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """LangChain-based orchestrator for coordinating multiple AI agents."""
    
    def __init__(self, config: Config):
        """Initialize the orchestrator."""
        self.config = config
        self.agents: Dict[AgentType, Any] = {}
        self.agent_configs: Dict[AgentType, AgentConfiguration] = {}
        self.agent_metrics: Dict[AgentType, AgentMetrics] = {}
        self.chat_sessions: Dict[str, ChatSession] = {}
        
        # Initialize LangChain LLM
        self.llm = AzureChatOpenAI(
            azure_endpoint=config.azure_openai_endpoint,
            api_version=config.azure_openai_api_version,
            deployment_name=config.azure_openai_deployment_name,
            temperature=0.7,
            azure_ad_token_provider=self._get_azure_token
        )
        
        # Orchestration prompt template
        self.orchestration_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_orchestration_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{query}")
        ])
        
        logger.info("MultiAgent orchestrator initialized")
    
    async def initialize(self):
        """Initialize all agents."""
        try:
            # Initialize Copilot Studio Agent 1 (General Conversation)
            copilot_agent_1 = CopilotStudioAgent(self.config, agent_id="copilot_1", specialization="general")
            await copilot_agent_1.initialize()
            self.agents[AgentType.COPILOT_STUDIO_1] = copilot_agent_1
            
            # Initialize Copilot Studio Agent 2 (Business Process)
            copilot_agent_2 = CopilotStudioAgent(self.config, agent_id="copilot_2", specialization="business_process")
            await copilot_agent_2.initialize()
            self.agents[AgentType.COPILOT_STUDIO_2] = copilot_agent_2
            
            # Initialize AI Foundry Agent 1 (Document Processing)
            ai_foundry_agent_1 = AIFoundryAgent(self.config, agent_id="ai_foundry_1", specialization="document_processing")
            await ai_foundry_agent_1.initialize()
            self.agents[AgentType.AI_FOUNDRY_1] = ai_foundry_agent_1
            
            # Initialize AI Foundry Agent 2 (Data Analysis)
            ai_foundry_agent_2 = AIFoundryAgent(self.config, agent_id="ai_foundry_2", specialization="data_analysis")
            await ai_foundry_agent_2.initialize()
            self.agents[AgentType.AI_FOUNDRY_2] = ai_foundry_agent_2
            
            # Initialize agent configurations
            await self._initialize_agent_configs()
            
            # Initialize metrics
            self._initialize_metrics()
            
            logger.info("All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            for agent in self.agents.values():
                if hasattr(agent, 'cleanup'):
                    await agent.cleanup()
            
            logger.info("Orchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def query_agent(
        self,
        agent_type: AgentType,
        request: AgentRequest,
        user_context: UserContext
    ) -> AgentResponse:
        """Query a specific agent."""
        start_time = datetime.utcnow()
        
        try:
            agent = self.agents.get(agent_type)
            if not agent:
                return AgentResponse(
                    success=False,
                    response="Agent not available",
                    agent_type=agent_type,
                    agent_id=f"{agent_type.value}_agent",
                    error="Agent not found or not initialized"
                )
            
            # Execute query
            response = await agent.query(request, user_context)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_agent_metrics(agent_type, True, execution_time)
            
            return response
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_agent_metrics(agent_type, False, execution_time)
            
            logger.error(f"Agent query failed for {agent_type.value}: {str(e)}")
            return AgentResponse(
                success=False,
                response="Agent query failed",
                agent_type=agent_type,
                agent_id=f"{agent_type.value}_agent",
                error=str(e),
                execution_time=execution_time
            )
    
    async def orchestrate_query(
        self,
        request: AgentRequest,
        user_context: UserContext
    ) -> OrchestrationResponse:
        """Orchestrate a query across multiple agents using LangChain."""
        start_time = datetime.utcnow()
        
        try:
            # Determine which agents to use
            selected_agents = await self._select_agents(request, user_context)
            
            if not selected_agents:
                return OrchestrationResponse(
                    success=False,
                    final_response="No suitable agents available for this query",
                    agents_used=[],
                    agent_responses=[],
                    execution_time=0.0,
                    strategy_used="none",
                    error="No agents selected"
                )
            
            # Execute orchestration strategy
            strategy = request.context.get('orchestration_strategy', 'adaptive')
            
            if strategy == 'sequential':
                result = await self._orchestrate_sequential(request, user_context, selected_agents)
            elif strategy == 'parallel':
                result = await self._orchestrate_parallel(request, user_context, selected_agents)
            else:  # adaptive
                result = await self._orchestrate_adaptive(request, user_context, selected_agents)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            result.strategy_used = strategy
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Orchestration failed: {str(e)}")
            
            return OrchestrationResponse(
                success=False,
                final_response="Orchestration failed",
                agents_used=[],
                agent_responses=[],
                execution_time=execution_time,
                strategy_used="failed",
                error=str(e)
            )
    
    async def _select_agents(
        self,
        request: AgentRequest,
        user_context: UserContext
    ) -> List[AgentType]:
        """Select appropriate agents for the query using LangChain."""
        
        # Use LLM to analyze query and suggest agents
        selection_prompt = f"""
        Analyze this user query and suggest which AI agents would be most appropriate to handle it.
        
        Available agents:
        - copilot_studio_1: General conversation, Q&A, and basic assistance
        - copilot_studio_2: Business process automation and workflow management
        - ai_foundry_1: Document processing, analysis, and content extraction
        - ai_foundry_2: Data analysis, statistics, and insights generation
        
        User query: {request.query}
        
        Respond with a JSON object containing:
        {{
            "suggested_agents": ["agent1", "agent2"],
            "reasoning": "Explanation of why these agents were selected"
        }}
        """
        
        try:
            llm_response = await self.llm.ainvoke([HumanMessage(content=selection_prompt)])
            
            # Parse LLM response (simplified - in production, use proper JSON parsing)
            suggested_agents = []
            
            # Default agent selection logic based on keywords
            query_lower = request.query.lower()
            
            # Document processing keywords
            if any(word in query_lower for word in ['document', 'pdf', 'file', 'text', 'extract', 'read']):
                suggested_agents.append(AgentType.AI_FOUNDRY_1)
            
            # Data analysis keywords
            if any(word in query_lower for word in ['data', 'analyze', 'statistics', 'chart', 'graph', 'report']):
                suggested_agents.append(AgentType.AI_FOUNDRY_2)
            
            # Business process keywords
            if any(word in query_lower for word in ['workflow', 'process', 'business', 'automation', 'task']):
                suggested_agents.append(AgentType.COPILOT_STUDIO_2)
            
            # General conversation keywords or fallback
            if not suggested_agents or any(word in query_lower for word in ['chat', 'help', 'question', 'hello', 'hi']):
                suggested_agents.append(AgentType.COPILOT_STUDIO_1)
            
            # Ensure we don't have duplicates and limit to 2 agents
            suggested_agents = list(set(suggested_agents))[:2]
            
            return suggested_agents
            
        except Exception as e:
            logger.warning(f"Agent selection failed, using default: {str(e)}")
            return [AgentType.COPILOT_STUDIO_1]  # Default fallback
    
    async def _orchestrate_sequential(
        self,
        request: AgentRequest,
        user_context: UserContext,
        agents: List[AgentType]
    ) -> OrchestrationResponse:
        """Execute agents sequentially, passing results between them."""
        
        agent_responses = []
        current_query = request.query
        current_context = request.context.copy()
        
        for agent_type in agents:
            # Create request for current agent
            agent_request = AgentRequest(
                query=current_query,
                context=current_context,
                parameters=request.parameters,
                session_id=request.session_id,
                history=request.history
            )
            
            # Query agent
            response = await self.query_agent(agent_type, agent_request, user_context)
            agent_responses.append(response)
            
            if not response.success:
                continue
            
            # Update context for next agent
            current_context['previous_response'] = response.response
            current_context['previous_agent'] = agent_type.value
        
        # Synthesize final response
        final_response = await self._synthesize_responses(agent_responses, request.query)
        
        return OrchestrationResponse(
            success=any(r.success for r in agent_responses),
            final_response=final_response,
            agents_used=agents,
            agent_responses=agent_responses,
            execution_time=0.0,  # Will be set by caller
            strategy_used="sequential"
        )
    
    async def _orchestrate_parallel(
        self,
        request: AgentRequest,
        user_context: UserContext,
        agents: List[AgentType]
    ) -> OrchestrationResponse:
        """Execute agents in parallel and combine results."""
        
        # Create tasks for parallel execution
        tasks = []
        for agent_type in agents:
            agent_request = AgentRequest(
                query=request.query,
                context=request.context,
                parameters=request.parameters,
                session_id=request.session_id,
                history=request.history
            )
            
            task = self.query_agent(agent_type, agent_request, user_context)
            tasks.append(task)
        
        # Execute all agents in parallel
        agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to AgentResponse objects
        valid_responses = []
        for i, response in enumerate(agent_responses):
            if isinstance(response, AgentResponse):
                valid_responses.append(response)
            else:
                # Create error response for failed agents
                error_response = AgentResponse(
                    success=False,
                    response="Agent failed",
                    agent_type=agents[i],
                    agent_id=f"{agents[i].value}_agent",
                    error=str(response) if isinstance(response, Exception) else "Unknown error"
                )
                valid_responses.append(error_response)
        
        # Synthesize final response
        final_response = await self._synthesize_responses(valid_responses, request.query)
        
        return OrchestrationResponse(
            success=any(r.success for r in valid_responses),
            final_response=final_response,
            agents_used=agents,
            agent_responses=valid_responses,
            execution_time=0.0,  # Will be set by caller
            strategy_used="parallel"
        )
    
    async def _orchestrate_adaptive(
        self,
        request: AgentRequest,
        user_context: UserContext,
        agents: List[AgentType]
    ) -> OrchestrationResponse:
        """Adaptive orchestration that chooses strategy based on query."""
        
        # Use LLM to determine best strategy
        strategy_prompt = f"""
        Given this query, determine the best orchestration strategy:
        
        Query: {request.query}
        Available agents: {[a.value for a in agents]}
        
        Choose between:
        - sequential: When agents need to build on each other's results
        - parallel: When agents can work independently and results should be combined
        
        Respond with just 'sequential' or 'parallel'.
        """
        
        try:
            llm_response = await self.llm.ainvoke([HumanMessage(content=strategy_prompt)])
            strategy = llm_response.content.strip().lower()
            
            if strategy == 'sequential':
                return await self._orchestrate_sequential(request, user_context, agents)
            else:
                return await self._orchestrate_parallel(request, user_context, agents)
                
        except Exception as e:
            logger.warning(f"Adaptive strategy selection failed: {str(e)}")
            # Default to parallel
            return await self._orchestrate_parallel(request, user_context, agents)
    
    async def _synthesize_responses(
        self,
        agent_responses: List[AgentResponse],
        original_query: str
    ) -> str:
        """Synthesize multiple agent responses into a coherent final response."""
        
        if not agent_responses:
            return "No responses received from agents."
        
        # Filter successful responses
        successful_responses = [r for r in agent_responses if r.success]
        
        if not successful_responses:
            return "All agents failed to provide a response."
        
        if len(successful_responses) == 1:
            return successful_responses[0].response
        
        # Use LLM to synthesize multiple responses
        synthesis_prompt = f"""
        Synthesize these responses from different AI agents into a coherent, comprehensive answer.
        
        Original query: {original_query}
        
        Agent responses:
        """
        
        for i, response in enumerate(successful_responses):
            synthesis_prompt += f"\nAgent {i+1} ({response.agent_type.value}): {response.response}\n"
        
        synthesis_prompt += "\nProvide a synthesized response that combines the best insights from all agents:"
        
        try:
            llm_response = await self.llm.ainvoke([HumanMessage(content=synthesis_prompt)])
            return llm_response.content
            
        except Exception as e:
            logger.error(f"Response synthesis failed: {str(e)}")
            # Fallback: concatenate responses
            return "\n\n".join([f"From {r.agent_type.value}: {r.response}" for r in successful_responses])
    
    async def create_chat_session(self, user_context: UserContext) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_context.user_id,
            title="New Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.chat_sessions[session_id] = session
        return session
    
    async def send_chat_message(
        self,
        session_id: str,
        message: ChatMessage,
        user_context: UserContext
    ) -> ChatResponse:
        """Send a message in a chat session."""
        try:
            session = self.chat_sessions.get(session_id)
            if not session:
                return ChatResponse(
                    message=message,
                    session_id=session_id,
                    success=False,
                    error="Session not found"
                )
            
            # Add user message to session
            session.messages.append(message)
            session.updated_at = datetime.utcnow()
            
            # Create agent request from message
            request = AgentRequest(
                query=message.content,
                context={"session_id": session_id},
                session_id=session_id,
                history=[
                    {"role": msg.role.value, "content": msg.content}
                    for msg in session.messages[-10:]  # Last 10 messages
                ]
            )
            
            # Orchestrate response
            orchestration_response = await self.orchestrate_query(request, user_context)
            
            # Create assistant message
            assistant_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=orchestration_response.final_response,
                timestamp=datetime.utcnow(),
                metadata={
                    "agents_used": [agent.value for agent in orchestration_response.agents_used],
                    "execution_time": orchestration_response.execution_time
                }
            )
            
            # Add assistant message to session
            session.messages.append(assistant_message)
            session.agents_used.extend([agent.value for agent in orchestration_response.agents_used])
            session.updated_at = datetime.utcnow()
            
            return ChatResponse(
                message=assistant_message,
                session_id=session_id,
                success=orchestration_response.success,
                metadata={
                    "agents_used": orchestration_response.agents_used,
                    "execution_time": orchestration_response.execution_time
                },
                agent_used="orchestrator"
            )
            
        except Exception as e:
            logger.error(f"Chat message failed: {str(e)}")
            return ChatResponse(
                message=message,
                session_id=session_id,
                success=False,
                error=str(e)
            )
    
    async def get_chat_history(self, session_id: str, user_context: UserContext) -> List[ChatMessage]:
        """Get chat history for a session."""
        session = self.chat_sessions.get(session_id)
        if not session or session.user_id != user_context.user_id:
            return []
        
        return session.messages
    
    def get_agent_capabilities(self, agent_type: AgentType) -> List[Dict[str, Any]]:
        """Get capabilities of a specific agent."""
        config = self.agent_configs.get(agent_type)
        if not config:
            return []
        
        return [
            {
                "name": cap.name,
                "description": cap.description,
                "input_types": cap.input_types,
                "output_types": cap.output_types
            }
            for cap in config.capabilities
        ]
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        total_requests = sum(metrics.total_requests for metrics in self.agent_metrics.values())
        successful_requests = sum(metrics.successful_requests for metrics in self.agent_metrics.values())
        
        return {
            "total_agents": len(self.agents),
            "active_sessions": len(self.chat_sessions),
            "total_requests": total_requests,
            "success_rate": successful_requests / max(total_requests, 1),
            "agent_metrics": {
                agent_type.value: {
                    "total_requests": metrics.total_requests,
                    "success_rate": metrics.successful_requests / max(metrics.total_requests, 1),
                    "average_response_time": metrics.average_response_time,
                    "uptime": metrics.uptime_percentage
                }
                for agent_type, metrics in self.agent_metrics.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_orchestration_system_prompt(self) -> str:
        """Get the system prompt for orchestration."""
        return """
        You are an AI agent orchestrator responsible for coordinating multiple specialized AI agents.
        Your role is to:
        1. Understand user queries and determine the best agents to handle them
        2. Coordinate agent interactions and synthesize responses
        3. Provide coherent, comprehensive answers to users
        
        Available agents:
        - Copilot Studio 1: General conversation, Q&A, and basic assistance
        - Copilot Studio 2: Business process automation and workflow management
        - AI Foundry 1: Document processing, analysis, and content extraction
        - AI Foundry 2: Data analysis, statistics, and insights generation
        
        Always prioritize user needs and provide the most helpful response possible.
        """
    
    async def _get_azure_token(self) -> str:
        """Get Azure AD token for authentication."""
        try:
            credential = self.config.get_azure_credential()
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        except Exception as e:
            logger.error(f"Failed to get Azure token: {str(e)}")
            raise
    
    async def _initialize_agent_configs(self):
        """Initialize agent configurations."""
        # This would typically load from configuration files or database
        # For now, we'll use hardcoded configurations
        
        self.agent_configs[AgentType.COPILOT_STUDIO_1] = AgentConfiguration(
            agent_type=AgentType.COPILOT_STUDIO_1,
            name="Copilot Studio Agent 1",
            description="Microsoft Copilot Studio bot for general conversation and Q&A",
            endpoint=self.config.copilot_studio_endpoint,
            api_version="v1",
            capabilities=[],
            priority=2
        )
        
        self.agent_configs[AgentType.COPILOT_STUDIO_2] = AgentConfiguration(
            agent_type=AgentType.COPILOT_STUDIO_2,
            name="Copilot Studio Agent 2",
            description="Microsoft Copilot Studio bot for business process automation",
            endpoint=self.config.copilot_studio_endpoint,
            api_version="v1",
            capabilities=[],
            priority=2
        )
        
        self.agent_configs[AgentType.AI_FOUNDRY_1] = AgentConfiguration(
            agent_type=AgentType.AI_FOUNDRY_1,
            name="AI Foundry Agent 1",
            description="Azure AI Foundry agent for document processing and content extraction",
            endpoint=self.config.ai_foundry_endpoint,
            api_version="v1",
            capabilities=[],
            priority=2
        )
        
        self.agent_configs[AgentType.AI_FOUNDRY_2] = AgentConfiguration(
            agent_type=AgentType.AI_FOUNDRY_2,
            name="AI Foundry Agent 2",
            description="Azure AI Foundry agent for data analysis and insights generation",
            endpoint=self.config.ai_foundry_endpoint,
            api_version="v1",
            capabilities=[],
            priority=3
        )
    
    def _initialize_metrics(self):
        """Initialize agent metrics."""
        for agent_type in AgentType:
            self.agent_metrics[agent_type] = AgentMetrics(
                agent_type=agent_type,
                agent_id=f"{agent_type.value}_agent"
            )
    
    def _update_agent_metrics(self, agent_type: AgentType, success: bool, execution_time: float):
        """Update agent metrics."""
        metrics = self.agent_metrics.get(agent_type)
        if not metrics:
            return
        
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update average response time
        if metrics.total_requests == 1:
            metrics.average_response_time = execution_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + execution_time) /
                metrics.total_requests
            )
        
        metrics.timestamp = datetime.utcnow()
