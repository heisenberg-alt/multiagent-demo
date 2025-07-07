"""
Main FastAPI application for the multiagent system.
This serves as the orchestrator using LangChain to coordinate multiple AI agents.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import asyncio
from contextlib import asynccontextmanager

# Azure imports
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError

# Authentication and authorization
from auth.auth_handler import AuthHandler
from auth.rbac_handler import RBACHandler

# Agent imports
from agents.orchestrator import MultiAgentOrchestrator
from agents.copilot_studio_agent import CopilotStudioAgent
from agents.ai_foundry_agent import AIFoundryAgent

# Models
from models.agent_models import AgentRequest, AgentResponse, AgentType, UserContext
from models.chat_models import ChatMessage, ChatSession

# Utilities
from utils.config import Config
from utils.logger import setup_logger
from utils.telemetry import TelemetryManager
from utils.m365_integration import M365Integration

# Initialize logging
logger = setup_logger(__name__)

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class AgentListResponse(BaseModel):
    agents: List[Dict[str, Any]]
    total: int

# Global variables
config: Config = None
auth_handler: AuthHandler = None
rbac_handler: RBACHandler = None
orchestrator: MultiAgentOrchestrator = None
telemetry: TelemetryManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global config, auth_handler, rbac_handler, orchestrator, telemetry
    
    try:
        # Initialize configuration
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Initialize telemetry
        telemetry = TelemetryManager(config.application_insights_connection_string)
        logger.info("Telemetry initialized")
        
        # Initialize authentication and authorization
        auth_handler = AuthHandler(config)
        rbac_handler = RBACHandler(config)
        logger.info("Authentication and authorization initialized")
        
        # Initialize the multiagent orchestrator
        orchestrator = MultiAgentOrchestrator(config)
        await orchestrator.initialize()
        logger.info("Multiagent orchestrator initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    finally:
        # Cleanup
        if orchestrator:
            await orchestrator.cleanup()
        if telemetry:
            telemetry.flush()
        logger.info("Application cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Multiagent System API",
    description="""
    A comprehensive multiagent orchestrator system featuring specialized AI agents.
    
    ## Agent Types
    
    ### Copilot Studio Agents
    - **COPILOT_STUDIO_1** (`copilot_1`): General conversation and Q&A
    - **COPILOT_STUDIO_2** (`copilot_2`): Business process automation and workflows
    
    ### AI Foundry Agents  
    - **AI_FOUNDRY_1** (`ai_foundry_1`): Document processing and content extraction
    - **AI_FOUNDRY_2** (`ai_foundry_2`): Data analysis and statistical modeling
    
    ## Features
    - **Intelligent Orchestration**: LangChain-powered agent coordination
    - **Specialized Capabilities**: Each agent optimized for specific use cases
    - **Azure Integration**: Full Azure AD authentication and RBAC
    - **Mock Mode**: Fallback responses for development and testing
    - **Performance Monitoring**: Comprehensive metrics and health checks
    
    ## Authentication
    All endpoints require Azure AD JWT tokens. Use the format:
    `Authorization: Bearer <your_jwt_token>`
    """,
    version="2.0.0",
    contact={
        "name": "Multiagent System Support",
        "email": "support@multiagent-system.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    tags_metadata=[
        {
            "name": "orchestration",
            "description": "Multi-agent orchestration endpoints"
        },
        {
            "name": "copilot-studio", 
            "description": "Copilot Studio agents for conversation and business processes"
        },
        {
            "name": "ai-foundry",
            "description": "AI Foundry agents for document processing and data analysis"
        },
        {
            "name": "agents",
            "description": "Agent management and health monitoring"
        },
        {
            "name": "chat",
            "description": "Chat session management"
        },
        {
            "name": "health",
            "description": "System health and monitoring"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        user_context = await auth_handler.validate_token(credentials.credentials)
        return user_context
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def check_agent_permission(user_context: UserContext, agent_type: AgentType):
    """Check if user has permission to access specific agent type."""
    if not rbac_handler.has_agent_permission(user_context, agent_type):
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied to {agent_type.value} agent"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Multiagent System API", "version": "1.0.0"}

@app.get("/agents", response_model=AgentListResponse)
async def list_agents(user_context: UserContext = Depends(get_current_user)):
    """List available agents for the user."""
    try:
        available_agents = []
        
        # Check permissions for each agent type
        for agent_type in AgentType:
            if rbac_handler.has_agent_permission(user_context, agent_type):
                agent_info = {
                    "type": agent_type.value,
                    "name": agent_type.value.replace("_", " ").title(),
                    "description": f"Access to {agent_type.value} capabilities",
                    "capabilities": orchestrator.get_agent_capabilities(agent_type)
                }
                available_agents.append(agent_info)
        
        return AgentListResponse(
            agents=available_agents,
            total=len(available_agents)
        )
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent list")

@app.post("/agents/{agent_type}/query")
async def query_agent(
    agent_type: AgentType,
    request: AgentRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Query a specific agent."""
    try:
        # Check permissions
        await check_agent_permission(user_context, agent_type)
        
        # Execute query through orchestrator
        response = await orchestrator.query_agent(
            agent_type=agent_type,
            request=request,
            user_context=user_context
        )
        
        # Log the interaction
        telemetry.track_agent_interaction(
            user_context.user_id,
            agent_type.value,
            request.query,
            response.success
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to query agent {agent_type.value}: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent query failed")

@app.post("/orchestrate")
async def orchestrate_multiagent_query(
    request: AgentRequest,
    user_context: UserContext = Depends(get_current_user)
):
    """Orchestrate a query across multiple agents."""
    try:
        # Execute orchestrated query
        response = await orchestrator.orchestrate_query(
            request=request,
            user_context=user_context
        )
        
        # Log the interaction
        telemetry.track_orchestration(
            user_context.user_id,
            request.query,
            response.agents_used,
            response.success
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to orchestrate query: {str(e)}")
        raise HTTPException(status_code=500, detail="Orchestration failed")

@app.post("/chat/sessions")
async def create_chat_session(
    user_context: UserContext = Depends(get_current_user)
):
    """Create a new chat session."""
    try:
        session = await orchestrator.create_chat_session(user_context)
        return {"session_id": session.session_id, "created_at": session.created_at}
    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@app.post("/chat/sessions/{session_id}/messages")
async def send_chat_message(
    session_id: str,
    message: ChatMessage,
    user_context: UserContext = Depends(get_current_user)
):
    """Send a message in a chat session."""
    try:
        response = await orchestrator.send_chat_message(
            session_id=session_id,
            message=message,
            user_context=user_context
        )
        
        # Log the interaction
        telemetry.track_chat_message(
            user_context.user_id,
            session_id,
            message.content,
            response.success
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send chat message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/chat/sessions/{session_id}/history")
async def get_chat_history(
    session_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get chat history for a session."""
    try:
        history = await orchestrator.get_chat_history(session_id, user_context)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@app.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    user_context: UserContext = Depends(get_current_user)
):
    """Get user permissions (admin only)."""
    try:
        # Check if user is admin
        if not rbac_handler.is_admin(user_context):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        permissions = rbac_handler.get_user_permissions(user_id)
        return {"user_id": user_id, "permissions": permissions}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user permissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve permissions")

@app.post("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: str,
    permissions: Dict[str, Any],
    user_context: UserContext = Depends(get_current_user)
):
    """Update user permissions (admin only)."""
    try:
        # Check if user is admin
        if not rbac_handler.is_admin(user_context):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = rbac_handler.update_user_permissions(user_id, permissions)
        
        # Log the permission change
        telemetry.track_permission_change(
            user_context.user_id,
            user_id,
            permissions
        )
        
        return {"user_id": user_id, "updated": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user permissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update permissions")

@app.get("/metrics")
async def get_metrics(
    user_context: UserContext = Depends(get_current_user)
):
    """Get system metrics (admin only)."""
    try:
        # Check if user is admin
        if not rbac_handler.is_admin(user_context):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        metrics = await orchestrator.get_system_metrics()
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    
    # Track the error
    if telemetry:
        telemetry.track_exception(exc)
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )
