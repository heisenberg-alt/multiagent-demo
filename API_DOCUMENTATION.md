# Multiagent System API Documentation

## Overview

The Multiagent System API provides endpoints for interacting with multiple specialized AI agents through a centralized orchestrator. The system now features **2 Copilot Studio agents** and **2 AI Foundry agents**, each with distinct specializations.

## Base URL
- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-app.azurecontainerapps.io`

## Authentication

All API endpoints require authentication using Azure AD (Entra ID) JWT tokens.

### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Token Acquisition
Use MSAL library to acquire tokens for the scope: `api://your-client-id/.default`

## Agent Types

The system features the following agent types:

### Copilot Studio Agents

#### COPILOT_STUDIO_1 (`copilot_studio_1`)
- **Specialization**: General conversation and Q&A
- **Agent ID**: `copilot_1`
- **Capabilities**:
  - General conversation
  - Question answering
  - Information retrieval
  - Basic assistance
  - Greeting handling

#### COPILOT_STUDIO_2 (`copilot_studio_2`)
- **Specialization**: Business process automation
- **Agent ID**: `copilot_2`
- **Capabilities**:
  - Workflow automation
  - Business process management
  - Task coordination
  - Process optimization
  - Approval workflows

### AI Foundry Agents

#### AI_FOUNDRY_1 (`ai_foundry_1`)
- **Specialization**: Document processing
- **Agent ID**: `ai_foundry_1`
- **Capabilities**:
  - Document extraction
  - Text classification
  - Content summarization
  - Document comparison

#### AI_FOUNDRY_2 (`ai_foundry_2`)
- **Specialization**: Data analysis
- **Agent ID**: `ai_foundry_2`
- **Capabilities**:
  - Data analysis
  - Predictive modeling
  - Data visualization
  - Statistical analysis

## API Endpoints

### 1. Orchestration Endpoints

#### POST /orchestrate
Orchestrate a request across multiple agents using intelligent agent selection.

**Request Body:**
```json
{
  "query": "Analyze this sales data and create a summary report",
  "preferred_agents": ["ai_foundry_2", "ai_foundry_1"],
  "orchestration_strategy": "adaptive",
  "context": {
    "task_type": "data_analysis",
    "priority": "high"
  },
  "session_id": "session_123",
  "max_agents": 3,
  "timeout": 30
}
```

**Response:**
```json
{
  "success": true,
  "final_response": "Based on the sales data analysis, here are the key insights...",
  "agents_used": ["ai_foundry_2", "ai_foundry_1"],
  "agent_responses": [
    {
      "success": true,
      "response": "Statistical analysis shows...",
      "agent_type": "ai_foundry_2",
      "agent_id": "ai_foundry_2",
      "confidence": 0.94,
      "execution_time": 2.5
    }
  ],
  "orchestration_metadata": {
    "strategy_applied": "adaptive",
    "agent_selection_reason": "Data analysis expertise"
  },
  "execution_time": 5.2,
  "timestamp": "2025-07-07T10:30:00Z",
  "strategy_used": "adaptive"
}
```

### 2. Direct Agent Endpoints

#### POST /agents/copilot_studio_1/query
Query the first Copilot Studio agent directly.

**Request Body:**
```json
{
  "query": "Hello, can you help me with general questions?",
  "context": {
    "conversation_type": "general"
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 500
  },
  "session_id": "session_123",
  "history": [
    {
      "role": "user",
      "content": "Previous message"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "Hello! I'm your Copilot Studio assistant specialized in general conversation...",
  "agent_type": "copilot_studio_1",
  "agent_id": "copilot_1",
  "confidence": 0.8,
  "metadata": {
    "bot_id": "your-bot-id",
    "conversation_id": "conv_123",
    "specialization": "general"
  },
  "usage": {
    "tokens_used": 45
  },
  "execution_time": 1.2,
  "timestamp": "2025-07-07T10:30:00Z"
}
```

#### POST /agents/copilot_studio_2/query
Query the second Copilot Studio agent (business process specialist).

**Request Body:**
```json
{
  "query": "Help me set up an approval workflow for expense reports",
  "context": {
    "workflow_type": "approval",
    "department": "finance"
  },
  "parameters": {
    "include_automation": true
  },
  "session_id": "session_123"
}
```

#### POST /agents/ai_foundry_1/query
Process a request with the first AI Foundry agent (document processing).

**Request Body:**
```json
{
  "query": "Extract key information from this contract document",
  "context": {
    "document_type": "contract",
    "extraction_fields": ["parties", "dates", "amounts"]
  },
  "file_data": {
    "content": "base64_encoded_content",
    "filename": "contract.pdf",
    "mime_type": "application/pdf"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "extracted_data": {
      "parties": ["Company A", "Company B"],
      "dates": ["2025-01-01", "2025-12-31"],
      "amounts": ["$100,000"]
    },
    "summary": "Contract between Company A and Company B for $100,000...",
    "confidence": 0.92
  },
  "agent_type": "ai_foundry_1",
  "agent_id": "ai_foundry_1",
  "metadata": {
    "specialization": "document_processing",
    "processing_time": 3.5
  },
  "execution_time": 3.5
}
```

#### POST /agents/ai_foundry_2/query
Process a request with the second AI Foundry agent (data analysis).

**Request Body:**
```json
{
  "query": "Analyze this sales data for trends and insights",
  "context": {
    "analysis_type": "trend_analysis",
    "time_period": "quarterly"
  },
  "data": {
    "format": "csv",
    "content": "date,sales,region\n2025-01-01,1000,North\n..."
  }
}
```

### 3. Agent Management Endpoints

#### GET /agents
List all available agents and their current status.

**Response:**
```json
{
  "agents": [
    {
      "agent_type": "copilot_studio_1",
      "agent_id": "copilot_1",
      "specialization": "general",
      "status": "healthy",
      "capabilities": [
        "general_conversation",
        "question_answering",
        "information_retrieval"
      ],
      "last_health_check": "2025-07-07T10:25:00Z"
    },
    {
      "agent_type": "copilot_studio_2", 
      "agent_id": "copilot_2",
      "specialization": "business_process",
      "status": "healthy",
      "capabilities": [
        "workflow_automation",
        "business_process_management",
        "task_coordination"
      ],
      "last_health_check": "2025-07-07T10:25:00Z"
    }
  ]
}
```

#### GET /agents/{agent_type}/capabilities
Get detailed capabilities for a specific agent.

**Response:**
```json
{
  "agent_type": "ai_foundry_1",
  "agent_id": "ai_foundry_1",
  "specialization": "document_processing",
  "capabilities": [
    {
      "name": "document_extraction",
      "description": "Extract structured data from unstructured documents",
      "input_types": ["pdf", "docx", "txt"],
      "output_types": ["structured_data", "json"],
      "parameters": {
        "max_file_size": "50MB",
        "supported_languages": ["en", "es", "fr"]
      }
    }
  ]
}
```

#### GET /agents/{agent_type}/health
Check the health status of a specific agent.

**Response:**
```json
{
  "agent_type": "copilot_studio_1",
  "agent_id": "copilot_1",
  "status": "healthy",
  "last_check": "2025-07-07T10:30:00Z",
  "response_time": 120,
  "error_rate": 0.02,
  "availability": 0.99,
  "details": {
    "endpoint_status": "connected",
    "authentication": "valid",
    "last_successful_request": "2025-07-07T10:29:45Z"
  }
}
```

### 4. Chat Session Endpoints

#### POST /chat/sessions
Create a new chat session.

**Request Body:**
```json
{
  "session_name": "Sales Analysis Discussion",
  "preferred_agents": ["ai_foundry_2"],
  "context": {
    "department": "sales",
    "project": "Q1_analysis"
  }
}
```

**Response:**
```json
{
  "session_id": "session_456",
  "created_at": "2025-07-07T10:30:00Z",
  "expires_at": "2025-07-07T12:30:00Z",
  "status": "active"
}
```

#### GET /chat/sessions/{session_id}/history
Retrieve chat history for a session.

#### POST /chat/sessions/{session_id}/messages
Send a message in a chat session.

### 5. Analytics Endpoints

#### GET /metrics
Get system metrics and agent usage statistics (admin only).

**Response:**
```json
{
  "system_metrics": {
    "total_requests": 5000,
    "successful_requests": 4750,
    "failed_requests": 250,
    "average_response_time": 2.3,
    "uptime": "99.5%"
  },
  "agent_stats": [
    {
      "agent_type": "copilot_studio_1",
      "total_requests": 1250,
      "successful_requests": 1200,
      "failed_requests": 50,
      "average_response_time": 1.8,
      "success_rate": 0.96
    }
  ]
}
```

### 6. Administrative Endpoints

#### GET /users/{user_id}/permissions
Get user permissions (admin only).

#### POST /users/{user_id}/permissions
Update user permissions (admin only).

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "AGENT_UNAVAILABLE",
    "message": "The requested agent is currently unavailable",
    "details": {
      "agent_type": "copilot_studio_1",
      "reason": "Connection timeout"
    },
    "timestamp": "2025-07-07T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED` (401): Valid JWT token required
- `INSUFFICIENT_PERMISSIONS` (403): User lacks required permissions
- `AGENT_UNAVAILABLE` (503): Agent is currently unavailable
- `INVALID_REQUEST` (400): Request format or parameters are invalid
- `ORCHESTRATION_FAILED` (500): Orchestration process failed
- `TIMEOUT` (408): Request timeout exceeded

## Rate Limiting

API requests are subject to rate limiting:
- **Per User**: 100 requests per minute
- **Per Agent**: 50 requests per minute per agent type
- **Orchestration**: 20 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625097600
```

## Webhooks

### Agent Status Changes
Register webhooks to receive notifications about agent status changes.

**Webhook Payload:**
```json
{
  "event": "agent.status.changed",
  "agent_type": "copilot_studio_1",
  "agent_id": "copilot_1",
  "old_status": "healthy",
  "new_status": "degraded",
  "timestamp": "2025-07-07T10:30:00Z"
}
```

## SDK Examples

### Python SDK
```python
from multiagent_client import MultiagentClient

client = MultiagentClient(
    base_url="https://your-app.azurecontainerapps.io",
    token_provider=azure_token_provider
)

# Orchestrated request
response = await client.orchestrate(
    query="Analyze this document and extract key insights",
    preferred_agents=["ai_foundry_1", "ai_foundry_2"]
)

# Direct agent query
response = await client.agents.copilot_studio_1.query(
    "Help me with general questions"
)
```

### JavaScript SDK
```javascript
import { MultiagentClient } from '@multiagent/client';

const client = new MultiagentClient({
  baseUrl: 'https://your-app.azurecontainerapps.io',
  tokenProvider: azureTokenProvider
});

// Orchestrated request
const response = await client.orchestrate({
  query: 'Analyze this document and extract key insights',
  preferredAgents: ['ai_foundry_1', 'ai_foundry_2']
});

// Direct agent query
const response = await client.agents.copilotStudio1.query(
  'Help me with general questions'
);
```

## Migration Guide

### From Previous Version

The agent architecture has been refactored. Here are the key changes:

#### Agent Type Mapping
| Old Agent Type | New Agent Type | Specialization |
|----------------|----------------|----------------|
| `PRO_CODE` | *Removed* | - |
| `AI_FOUNDRY_LOW_CODE` | *Removed* | - |
| `COPILOT_STUDIO` | `COPILOT_STUDIO_1` | General conversation |
| `AI_FOUNDRY_HIGH_CODE` | `AI_FOUNDRY_2` | Data analysis |
| *New* | `COPILOT_STUDIO_2` | Business processes |
| *New* | `AI_FOUNDRY_1` | Document processing |

#### Breaking Changes
1. **Agent Endpoints**: Update URLs to use new agent type names
2. **Response Format**: `agent_id` field added to all responses
3. **Capabilities**: New capability structure with specialization
4. **Orchestration**: Updated agent selection logic

#### Migration Steps
1. Update client code to use new agent type names
2. Update any hardcoded agent references
3. Test with new agent capabilities
4. Update error handling for new error codes

## Quick Start Examples

### Basic Orchestration
```bash
# Simple orchestration request
curl -X POST "http://localhost:8000/orchestrate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze this sales report and provide insights",
    "orchestration_strategy": "adaptive"
  }'
```

### Document Processing
```bash
# Direct document processing
curl -X POST "http://localhost:8000/agents/ai_foundry_1/query" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Extract key information from this contract",
    "context": {
      "document_type": "contract",
      "extraction_fields": ["parties", "dates", "amounts"]
    }
  }'
```

### Business Process Automation
```bash
# Business process query
curl -X POST "http://localhost:8000/agents/copilot_studio_2/query" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create an expense approval workflow",
    "context": {
      "workflow_type": "approval",
      "department": "finance"
    }
  }'
```

### Chat Session Management
```bash
# Create a chat session
curl -X POST "http://localhost:8000/chat/sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "Data Analysis Session",
    "preferred_agents": ["ai_foundry_2"]
  }'

# Send message in session
curl -X POST "http://localhost:8000/chat/sessions/SESSION_ID/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Show me the trends in this data",
    "role": "user"
  }'
```

## Advanced Usage Patterns

### Multi-Agent Workflow
```python
import asyncio
from multiagent_client import MultiAgentClient

async def document_analysis_workflow():
    client = MultiAgentClient(
        base_url="http://localhost:8000",
        token_provider=get_azure_token
    )
    
    # Step 1: Extract document content
    extraction_response = await client.agents.ai_foundry_1.query(
        "Extract text and structure from this PDF document",
        context={"document_type": "report"}
    )
    
    # Step 2: Analyze extracted data
    analysis_response = await client.agents.ai_foundry_2.query(
        f"Analyze this data: {extraction_response.response}",
        context={"analysis_type": "comprehensive"}
    )
    
    # Step 3: Generate business recommendations
    recommendations = await client.agents.copilot_studio_2.query(
        f"Based on this analysis, what business actions should we take? {analysis_response.response}",
        context={"workflow_type": "recommendation"}
    )
    
    return {
        "extracted_data": extraction_response.response,
        "analysis": analysis_response.response,
        "recommendations": recommendations.response
    }
```

### Error Handling and Retries
```python
import asyncio
from typing import Optional

async def robust_agent_query(client, agent_type: str, query: str, max_retries: int = 3) -> Optional[dict]:
    """Robust agent query with retry logic"""
    for attempt in range(max_retries):
        try:
            if agent_type == "orchestrate":
                response = await client.orchestrate(query)
            else:
                response = await getattr(client.agents, agent_type).query(query)
            
            if response.success:
                return response
            else:
                print(f"Attempt {attempt + 1} failed: {response.error}")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {str(e)}")
            
        # Exponential backoff
        await asyncio.sleep(2 ** attempt)
    
    return None
```

### Performance Monitoring
```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def monitor_agent_performance(agent_name: str):
    """Context manager for monitoring agent performance"""
    start_time = time.time()
    try:
        print(f"Starting {agent_name} request...")
        yield
    except Exception as e:
        print(f"Error in {agent_name}: {str(e)}")
        raise
    finally:
        duration = time.time() - start_time
        print(f"{agent_name} completed in {duration:.2f} seconds")

# Usage
async def monitored_query():
    async with monitor_agent_performance("AI Foundry Document Processing"):
        response = await client.agents.ai_foundry_1.query(
            "Process this document",
            context={"priority": "high"}
        )
```

## Best Practices

### Authentication
- Always use HTTPS in production
- Implement proper token refresh logic
- Store tokens securely (avoid hardcoding)
- Use minimal required scopes

### Request Optimization
- Use appropriate agent types for specific tasks
- Provide relevant context in requests
- Set reasonable timeouts
- Implement retry logic for transient failures

### Resource Management
- Close HTTP connections properly
- Implement connection pooling for high-volume usage
- Monitor rate limits and implement backoff
- Use async/await for concurrent requests

### Error Handling
- Implement comprehensive error handling
- Log errors with sufficient detail
- Provide meaningful error messages to users
- Implement graceful degradation

## Performance Considerations

### Latency Optimization
- Use direct agent endpoints when possible
- Implement client-side caching for repeated queries
- Use connection pooling
- Consider geographic proximity to Azure regions

### Scalability
- Implement rate limiting in client applications
- Use connection pooling for high-throughput scenarios
- Monitor and optimize payload sizes
- Consider async processing for long-running tasks

### Cost Management
- Monitor token usage across agents
- Implement request deduplication
- Use appropriate timeout values
- Consider caching for frequently requested data
