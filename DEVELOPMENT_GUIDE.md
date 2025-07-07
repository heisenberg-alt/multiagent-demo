# Development Guide

## Overview

This guide provides comprehensive information for developers working with the Multiagent System. It covers the new agent architecture, development workflows, testing strategies, and best practices.

## System Architecture

### Current Agent Lineup (Post-Refactoring)

The system now features **4 specialized agents**:

```
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Orchestrator                    │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Copilot Studio  │ Copilot Studio  │      AI Foundry         │
│ Agent 1         │ Agent 2         │      Agents             │
│ (General)       │ (Business)      │                         │
│                 │                 │ Agent 1: Document Proc  │
│ agent_id:       │ agent_id:       │ agent_id: ai_foundry_1  │
│ copilot_1       │ copilot_2       │                         │
│                 │                 │ Agent 2: Data Analysis  │
│                 │                 │ agent_id: ai_foundry_2  │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Key Changes from Previous Version

| Component | Before | After | Change Type |
|-----------|--------|-------|-------------|
| **Agent Types** | `PRO_CODE`, `AI_FOUNDRY_LOW_CODE`, `COPILOT_STUDIO`, `AI_FOUNDRY_HIGH_CODE` | `COPILOT_STUDIO_1`, `COPILOT_STUDIO_2`, `AI_FOUNDRY_1`, `AI_FOUNDRY_2` | **Breaking** |
| **Agent IDs** | Static agent names | Configurable `agent_id` parameter | **Enhancement** |
| **Specializations** | Generic capabilities | Specialized capabilities per agent | **Enhancement** |
| **Orchestrator** | Basic agent selection | Intelligent selection based on specialization | **Enhancement** |

## Development Environment Setup

### Prerequisites

1. **Python 3.9+** with virtual environment support
2. **Node.js 18+** for frontend development
3. **Azure CLI** for cloud integration
4. **VS Code** (recommended) with Python and TypeScript extensions
5. **Git** for version control

### Local Development Setup

#### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd multiagent-demo

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

#### 2. Configuration Files

Create test configuration for local development:

**`backend/test_config.py`** (for testing):
```python
class SimpleConfig:
    def __init__(self):
        self.azure_tenant_id = "test-tenant"
        self.azure_client_id = "test-client"
        self.azure_openai_endpoint = ""
        self.azure_openai_api_version = "2023-05-15"
        self.azure_openai_deployment_name = "gpt-4"
        self.copilot_studio_endpoint = ""
        self.ai_foundry_endpoint = ""
        # ... other config
```

**`backend/.env`** (for real Azure integration):
```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_OPENAI_ENDPOINT=your-openai-endpoint
COPILOT_STUDIO_ENDPOINT=your-copilot-endpoint
AI_FOUNDRY_ENDPOINT=your-ai-foundry-endpoint
```

#### 3. Running the Application

**Backend (Terminal 1):**
```bash
cd backend
python main.py
# Server runs on http://localhost:8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
# App runs on http://localhost:3000
```

## Agent Development

### Agent Base Interface

All agents should implement the following interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from models.agent_models import AgentRequest, AgentResponse, UserContext

class BaseAgent(ABC):
    def __init__(self, config: Config, agent_id: str, specialization: str):
        self.config = config
        self.agent_id = agent_id
        self.specialization = specialization
        self.capabilities = self._get_specialized_capabilities()
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup resources."""
        pass
    
    @abstractmethod
    def _get_specialized_capabilities(self) -> List[str]:
        """Get capabilities based on specialization."""
        pass
```

### Creating a New Agent

#### 1. Agent Class Implementation

```python
# backend/agents/my_new_agent.py
from typing import Dict, Any, List, Optional
from models.agent_models import AgentRequest, AgentResponse, AgentType, UserContext
from utils.config import Config
import logging

logger = logging.getLogger(__name__)

class MyNewAgent:
    def __init__(self, config: Config, agent_id: str, specialization: str):
        self.config = config
        self.agent_id = agent_id
        self.specialization = specialization
        self.capabilities = self._get_specialized_capabilities()
        
    def _get_specialized_capabilities(self) -> List[str]:
        """Define agent capabilities based on specialization."""
        if self.specialization == "my_specialty":
            return ["capability_1", "capability_2", "capability_3"]
        return ["default_capability"]
    
    async def initialize(self) -> bool:
        """Initialize the agent."""
        try:
            # Setup connections, validate config, etc.
            logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            return False
    
    async def query(self, request: AgentRequest, user_context: UserContext) -> AgentResponse:
        """Process a query request."""
        start_time = datetime.utcnow()
        
        try:
            # Process the request
            response_text = await self._process_query(request.query, request.context)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResponse(
                success=True,
                response=response_text,
                agent_type=AgentType.MY_NEW_AGENT,  # Add to enum
                agent_id=self.agent_id,
                confidence=0.8,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Query failed for agent {self.agent_id}: {e}")
            return AgentResponse(
                success=False,
                response="Agent is currently unavailable",
                agent_type=AgentType.MY_NEW_AGENT,
                agent_id=self.agent_id,
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def _process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Implement your agent's core logic here."""
        # Your implementation here
        return f"Processed: {query}"
```

#### 2. Update Agent Types

```python
# backend/models/agent_models.py
class AgentType(Enum):
    COPILOT_STUDIO_1 = "copilot_studio_1"
    COPILOT_STUDIO_2 = "copilot_studio_2"
    AI_FOUNDRY_1 = "ai_foundry_1"
    AI_FOUNDRY_2 = "ai_foundry_2"
    MY_NEW_AGENT = "my_new_agent"  # Add your new agent
    ORCHESTRATOR = "orchestrator"
```

#### 3. Register in Orchestrator

```python
# backend/agents/orchestrator.py
async def initialize(self):
    """Initialize all agents."""
    try:
        # ... existing agents ...
        
        # Add your new agent
        new_agent = MyNewAgent(self.config, agent_id="new_1", specialization="my_specialty")
        await new_agent.initialize()
        self.agents[AgentType.MY_NEW_AGENT] = new_agent
        
        logger.info("All agents initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise
```

#### 4. Update RBAC Permissions

```python
# backend/auth/rbac_handler.py
AGENT_PERMISSIONS = {
    AgentType.COPILOT_STUDIO_1: ["copilot_studio"],
    AgentType.COPILOT_STUDIO_2: ["copilot_studio"],
    AgentType.AI_FOUNDRY_1: ["ai_foundry"],
    AgentType.AI_FOUNDRY_2: ["ai_foundry"],
    AgentType.MY_NEW_AGENT: ["my_new_agent"],  # Add permission
    AgentType.ORCHESTRATOR: ["orchestrator"]
}
```

## Testing

### Test Structure

```
tests/
├── unit/
│   ├── test_agents/
│   │   ├── test_copilot_studio_agent.py
│   │   ├── test_ai_foundry_agent.py
│   │   └── test_my_new_agent.py
│   ├── test_orchestrator.py
│   └── test_models.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_agent_integration.py
└── fixtures/
    ├── mock_data.py
    └── test_config.py
```

### Writing Agent Tests

#### Unit Test Example

```python
# tests/unit/test_agents/test_my_new_agent.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from agents.my_new_agent import MyNewAgent
from models.agent_models import AgentRequest, UserContext
from test_config import SimpleConfig

@pytest.fixture
def mock_config():
    return SimpleConfig()

@pytest.fixture
def agent(mock_config):
    return MyNewAgent(mock_config, agent_id="test_agent", specialization="my_specialty")

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initialization."""
    result = await agent.initialize()
    assert result is True
    assert agent.agent_id == "test_agent"
    assert agent.specialization == "my_specialty"

@pytest.mark.asyncio
async def test_agent_query_success(agent):
    """Test successful query processing."""
    request = AgentRequest(query="test query", context={"test": "context"})
    user_context = UserContext(
        user_id="test_user",
        username="test",
        email="test@example.com",
        name="Test User",
        tenant_id="test_tenant"
    )
    
    response = await agent.query(request, user_context)
    
    assert response.success is True
    assert response.agent_id == "test_agent"
    assert "Processed: test query" in response.response
```

#### Integration Test Example

```python
# tests/integration/test_agent_integration.py
import pytest
from agents.orchestrator import MultiAgentOrchestrator
from models.agent_models import OrchestrationRequest, UserContext
from test_config import SimpleConfig

@pytest.mark.asyncio
async def test_orchestrator_with_new_agent():
    """Test orchestrator integration with new agent."""
    config = SimpleConfig()
    orchestrator = MultiAgentOrchestrator(config)
    await orchestrator.initialize()
    
    # Verify agent is registered
    assert AgentType.MY_NEW_AGENT in orchestrator.agents
    
    # Test orchestration
    request = OrchestrationRequest(
        query="test query for my new agent",
        preferred_agents=[AgentType.MY_NEW_AGENT]
    )
    
    user_context = UserContext(
        user_id="test_user",
        username="test",
        email="test@example.com", 
        name="Test User",
        tenant_id="test_tenant"
    )
    
    response = await orchestrator.orchestrate(request, user_context)
    assert response.success is True
    assert AgentType.MY_NEW_AGENT in response.agents_used
```

### Running Tests

```bash
# Run all tests
cd backend
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_agents/test_my_new_agent.py

# Run with coverage
python -m pytest --cov=agents --cov-report=html

# Run integration tests only
python -m pytest tests/integration/
```

### Test Configuration

Use the `test_config.py` for mock configurations:

```python
# test_config.py
class SimpleConfig:
    def __init__(self):
        # Mock all required configuration
        self.azure_tenant_id = "test-tenant"
        self.copilot_studio_endpoint = ""
        self.ai_foundry_endpoint = ""
        # ... other mock settings
        
    def get_azure_credential(self):
        """Return mock credential."""
        from unittest.mock import MagicMock
        return MagicMock()
```

## Frontend Development

### Agent Types in Frontend

Update frontend types to match backend:

```typescript
// frontend/src/types/agent.ts
export enum AgentType {
  COPILOT_STUDIO_1 = 'copilot_studio_1',
  COPILOT_STUDIO_2 = 'copilot_studio_2', 
  AI_FOUNDRY_1 = 'ai_foundry_1',
  AI_FOUNDRY_2 = 'ai_foundry_2',
  MY_NEW_AGENT = 'my_new_agent',
  ORCHESTRATOR = 'orchestrator'
}

export interface AgentInfo {
  agentType: AgentType;
  agentId: string;
  specialization: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  capabilities: string[];
}
```

### Redux Store Updates

```typescript
// frontend/src/store/slices/agentSlice.ts
const agentSlice = createSlice({
  name: 'agent',
  initialState: {
    availableAgents: [] as AgentInfo[],
    selectedAgent: null as AgentType | null,
    // ... other state
  },
  reducers: {
    setAvailableAgents: (state, action) => {
      state.availableAgents = action.payload;
    },
    selectAgent: (state, action) => {
      state.selectedAgent = action.payload;
    }
    // ... other reducers
  }
});
```

## API Integration

### Backend API Endpoints

The refactored system provides these key endpoints:

```python
# main.py - FastAPI routes
@app.post("/api/v1/orchestrate")
async def orchestrate_request(request: OrchestrationRequest):
    """Orchestrate request across agents."""
    pass

@app.post("/api/v1/agents/copilot-studio-1/query")
async def query_copilot_studio_1(request: AgentRequest):
    """Query Copilot Studio Agent 1."""
    pass

@app.post("/api/v1/agents/copilot-studio-2/query") 
async def query_copilot_studio_2(request: AgentRequest):
    """Query Copilot Studio Agent 2."""
    pass

@app.post("/api/v1/agents/ai-foundry-1/process")
async def process_ai_foundry_1(request: Dict[str, Any]):
    """Process with AI Foundry Agent 1."""
    pass

@app.post("/api/v1/agents/ai-foundry-2/process")
async def process_ai_foundry_2(request: Dict[str, Any]):
    """Process with AI Foundry Agent 2."""
    pass

@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents."""
    pass
```

### Frontend API Services

```typescript
// frontend/src/services/agentService.ts
class AgentService {
  async orchestrateRequest(request: OrchestrationRequest): Promise<OrchestrationResponse> {
    const response = await fetch('/api/v1/orchestrate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getToken()}`
      },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  async queryAgent(agentType: AgentType, request: AgentRequest): Promise<AgentResponse> {
    const endpoint = this.getAgentEndpoint(agentType);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getToken()}`
      },
      body: JSON.stringify(request)
    });
    return response.json();
  }

  private getAgentEndpoint(agentType: AgentType): string {
    const endpoints = {
      [AgentType.COPILOT_STUDIO_1]: '/api/v1/agents/copilot-studio-1/query',
      [AgentType.COPILOT_STUDIO_2]: '/api/v1/agents/copilot-studio-2/query',
      [AgentType.AI_FOUNDRY_1]: '/api/v1/agents/ai-foundry-1/process',
      [AgentType.AI_FOUNDRY_2]: '/api/v1/agents/ai-foundry-2/process'
    };
    return endpoints[agentType];
  }
}
```

## Deployment

### Local Deployment

```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend  
cd frontend
npm run build
npm run start
```

### Azure Deployment

```bash
# Using Azure Developer CLI
azd auth login
azd up

# Manual deployment
az login
az group create --name multiagent-rg --location eastus
az deployment group create --resource-group multiagent-rg --template-file infra/main.bicep
```

### Docker Deployment

```dockerfile
# Dockerfile (backend)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t multiagent-backend .
docker run -p 8000:8000 multiagent-backend
```

## Best Practices

### Code Organization

1. **Separation of Concerns**: Keep agent logic separate from orchestration
2. **Configuration Management**: Use environment variables for settings
3. **Error Handling**: Implement comprehensive error handling and logging
4. **Testing**: Write tests for all agent functionality
5. **Documentation**: Document agent capabilities and usage patterns

### Performance Optimization

1. **Async Operations**: Use async/await for all I/O operations
2. **Connection Pooling**: Reuse HTTP connections where possible
3. **Caching**: Cache frequently accessed data
4. **Monitoring**: Implement health checks and metrics

### Security Considerations

1. **Authentication**: Always verify JWT tokens
2. **Authorization**: Check user permissions for agent access  
3. **Input Validation**: Sanitize all inputs, especially file uploads
4. **Secrets Management**: Use Azure Key Vault for sensitive data
5. **Audit Logging**: Log all agent interactions for security auditing

## Troubleshooting

### Common Development Issues

#### Import Errors
```bash
# Fix: Use absolute imports and check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project/backend"
```

#### Agent Not Found
```python
# Check agent registration in orchestrator
logger.info(f"Registered agents: {list(orchestrator.agents.keys())}")
```

#### Authentication Failures
```bash
# Verify Azure configuration
az account show
az ad app list --display-name "your-app-name"
```

#### Mock Mode Issues
```python
# Ensure test configuration is properly set
config = SimpleConfig()
assert config.copilot_studio_endpoint == ""  # Should be empty for mock mode
```

### Debugging Tools

1. **VS Code Debugger**: Set breakpoints in agent code
2. **FastAPI Docs**: Use `/docs` endpoint for API testing
3. **Azure CLI**: Debug Azure service connections
4. **Browser DevTools**: Debug frontend API calls

---

For additional support, see the [API Documentation](./API_DOCUMENTATION.md) and [Agent Documentation](./AGENT_DOCUMENTATION.md).
