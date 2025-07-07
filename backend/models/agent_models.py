"""
Pydantic models for agent-related data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system."""
    COPILOT_STUDIO_1 = "copilot_studio_1"
    COPILOT_STUDIO_2 = "copilot_studio_2"
    AI_FOUNDRY_1 = "ai_foundry_1"
    AI_FOUNDRY_2 = "ai_foundry_2"
    ORCHESTRATOR = "orchestrator"

class AgentCapability(BaseModel):
    """Represents a capability of an agent."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any] = {}

class UserContext(BaseModel):
    """User context information."""
    user_id: str
    username: str
    email: str
    name: str
    tenant_id: str
    roles: List[str] = []
    groups: List[str] = []
    app_roles: Dict[str, Any] = {}
    token_type: str = "jwt"
    expires_at: Optional[datetime] = None
    profile: Dict[str, Any] = {}

class AgentRequest(BaseModel):
    """Request to an agent."""
    query: str = Field(..., description="The user's query or request")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific parameters")
    session_id: Optional[str] = Field(None, description="Chat session ID if applicable")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response")
    temperature: Optional[float] = Field(None, description="Temperature for response generation")
    tools: List[str] = Field(default_factory=list, description="Available tools for the agent")

class AgentResponse(BaseModel):
    """Response from an agent."""
    success: bool
    response: str
    agent_type: AgentType
    agent_id: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    tools_used: List[str] = Field(default_factory=list)

class OrchestrationRequest(BaseModel):
    """Request for orchestrated multi-agent interaction."""
    query: str
    preferred_agents: List[AgentType] = Field(default_factory=list)
    orchestration_strategy: str = "adaptive"  # adaptive, sequential, parallel
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    max_agents: int = 3
    timeout: int = 30  # seconds

class OrchestrationResponse(BaseModel):
    """Response from orchestrated multi-agent interaction."""
    success: bool
    final_response: str
    agents_used: List[AgentType]
    agent_responses: List[AgentResponse]
    orchestration_metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    strategy_used: str
    error: Optional[str] = None

class AgentConfiguration(BaseModel):
    """Configuration for an agent."""
    agent_type: AgentType
    name: str
    description: str
    endpoint: str
    api_version: str
    authentication: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[AgentCapability] = Field(default_factory=list)
    enabled: bool = True
    priority: int = 1  # Higher priority agents are preferred
    rate_limit: Dict[str, int] = Field(default_factory=dict)
    timeout: int = 30

class AgentHealth(BaseModel):
    """Health status of an agent."""
    agent_type: AgentType
    agent_id: str
    status: str  # healthy, degraded, unhealthy, unknown
    last_check: datetime
    response_time: Optional[float] = None
    error_rate: Optional[float] = None
    availability: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class AgentMetrics(BaseModel):
    """Metrics for an agent."""
    agent_type: AgentType
    agent_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_24h_requests: int = 0
    current_load: float = 0.0
    uptime_percentage: float = 100.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentEvent(BaseModel):
    """Event from an agent."""
    agent_type: AgentType
    agent_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = "info"  # debug, info, warning, error, critical
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ToolDefinition(BaseModel):
    """Definition of a tool that agents can use."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    endpoint: Optional[str] = None
    implementation: Optional[str] = None
    required_permissions: List[str] = Field(default_factory=list)

class AgentTool(BaseModel):
    """Tool available to an agent."""
    tool: ToolDefinition
    enabled: bool = True
    configuration: Dict[str, Any] = Field(default_factory=dict)

class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    turn_id: str
    user_message: str
    agent_response: AgentResponse
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    feedback: Optional[Dict[str, Any]] = None

class AgentPipeline(BaseModel):
    """Definition of an agent pipeline."""
    pipeline_id: str
    name: str
    description: str
    agents: List[AgentType]
    execution_strategy: str = "sequential"  # sequential, parallel, conditional
    conditions: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

class AgentAnalytics(BaseModel):
    """Analytics data for agents."""
    time_period: str
    agent_type: Optional[AgentType] = None
    total_interactions: int
    successful_interactions: int
    average_satisfaction: Optional[float] = None
    top_queries: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    user_distribution: Dict[str, int] = Field(default_factory=dict)
    error_patterns: List[Dict[str, Any]] = Field(default_factory=list)
