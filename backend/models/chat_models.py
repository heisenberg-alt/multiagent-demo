"""
Pydantic models for chat-related data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    """Types of chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"

class MessageRole(Enum):
    """Roles in a chat conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """A chat message."""
    id: Optional[str] = None
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    name: Optional[str] = None  # For function/tool messages
    
class ChatSession(BaseModel):
    """A chat session."""
    session_id: str
    user_id: str
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    agents_used: List[str] = Field(default_factory=list)
    total_tokens: int = 0
    
class ChatResponse(BaseModel):
    """Response to a chat message."""
    message: ChatMessage
    session_id: str
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, Any] = Field(default_factory=dict)
    agent_used: Optional[str] = None
    
class ChatSettings(BaseModel):
    """Settings for a chat session."""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_message: Optional[str] = None
    tools: List[str] = Field(default_factory=list)
    agent_preferences: Dict[str, Any] = Field(default_factory=dict)
    
class ChatHistory(BaseModel):
    """Chat history for a session."""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    date_range: Dict[str, datetime]
    agents_involved: List[str] = Field(default_factory=list)
    
class ChatSummary(BaseModel):
    """Summary of a chat session."""
    session_id: str
    user_id: str
    title: str
    summary: str
    key_topics: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None
    message_count: int
    duration: Optional[float] = None  # in minutes
    agents_used: List[str] = Field(default_factory=list)
    created_at: datetime
    last_activity: datetime
    
class ChatAnalytics(BaseModel):
    """Analytics for chat interactions."""
    total_sessions: int
    total_messages: int
    average_session_length: float
    most_used_agents: List[Dict[str, Any]] = Field(default_factory=list)
    common_topics: List[Dict[str, Any]] = Field(default_factory=list)
    user_satisfaction: Optional[float] = None
    response_time_stats: Dict[str, float] = Field(default_factory=dict)
    time_period: str
    
class ChatFeedback(BaseModel):
    """Feedback on a chat interaction."""
    session_id: str
    message_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_used: Optional[str] = None
    
class ChatTemplate(BaseModel):
    """Template for chat prompts."""
    template_id: str
    name: str
    description: str
    template: str
    variables: List[str] = Field(default_factory=list)
    category: str
    tags: List[str] = Field(default_factory=list)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = False
    
class ChatIntent(BaseModel):
    """Detected intent in a chat message."""
    intent: str
    confidence: float
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    suggested_agent: Optional[str] = None
    
class ChatContext(BaseModel):
    """Context for a chat conversation."""
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    current_task: Optional[str] = None
    workspace_context: Dict[str, Any] = Field(default_factory=dict)
    agent_memory: Dict[str, Any] = Field(default_factory=dict)
    external_context: Dict[str, Any] = Field(default_factory=dict)
    
class ChatConfiguration(BaseModel):
    """Configuration for chat functionality."""
    default_agent: str
    auto_agent_selection: bool = True
    multi_agent_orchestration: bool = True
    context_window_size: int = 4000
    max_session_duration: int = 3600  # seconds
    enable_feedback: bool = True
    enable_analytics: bool = True
    custom_prompts: Dict[str, str] = Field(default_factory=dict)
    
class ChatExport(BaseModel):
    """Export data for a chat session."""
    session: ChatSession
    messages: List[ChatMessage]
    analytics: Optional[ChatAnalytics] = None
    feedback: List[ChatFeedback] = Field(default_factory=list)
    export_format: str = "json"
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    exported_by: str
