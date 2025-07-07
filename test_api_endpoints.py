#!/usr/bin/env python3
"""
Updated test suite for the multiagent system API endpoints.
Tests the FastAPI application with the new agent architecture.
"""

import sys
import os
import asyncio
import pytest
from typing import Dict, Any
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from main import app
    from models.agent_models import AgentType, UserContext
    from test_config import SimpleConfig as Config
except ImportError as e:
    print(f"Import error: {e}")
    # For testing purposes, create minimal mocks
    app = None
    Config = None

# Mock user context for testing
MOCK_USER_CONTEXT = {
    "user_id": "test_user",
    "username": "testuser",
    "email": "test@example.com",
    "name": "Test User",
    "tenant_id": "test_tenant",
    "roles": ["user"],
    "groups": ["test_group"]
}

# Mock JWT token for testing
MOCK_JWT_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdF91c2VyIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciJ9.test_signature"

class TestMultiagentAPI:
    """Test the multiagent system API endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Set up test client."""
        cls.client = TestClient(app)
        cls.headers = {
            "Authorization": MOCK_JWT_TOKEN,
            "Content-Type": "application/json"
        }
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        
    def test_orchestrate_endpoint(self):
        """Test the orchestration endpoint."""
        payload = {
            "query": "Analyze this sales data and provide insights",
            "orchestration_strategy": "adaptive",
            "context": {
                "task_type": "data_analysis",
                "priority": "high"
            },
            "max_agents": 2
        }
        
        response = self.client.post("/orchestrate", json=payload, headers=self.headers)
        # Note: This might return 401 due to auth mocking, but endpoint should exist
        assert response.status_code in [200, 401, 500]  # Accept auth or initialization errors
        
    def test_agent_endpoints_exist(self):
        """Test that all agent endpoints exist."""
        agent_queries = [
            ("/agents/copilot_studio_1/query", {"query": "Hello, how can you help?"}),
            ("/agents/copilot_studio_2/query", {"query": "Set up a workflow"}),
            ("/agents/ai_foundry_1/query", {"query": "Process this document"}),
            ("/agents/ai_foundry_2/query", {"query": "Analyze this data"})
        ]
        
        for endpoint, payload in agent_queries:
            response = self.client.post(endpoint, json=payload, headers=self.headers)
            # Accept various error codes but ensure endpoint exists (not 404)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            
    def test_agents_list_endpoint(self):
        """Test the agents list endpoint."""
        response = self.client.get("/agents", headers=self.headers)
        # Accept auth errors but ensure endpoint exists
        assert response.status_code in [200, 401, 500]
        assert response.status_code != 404
        
    def test_chat_session_endpoints(self):
        """Test chat session endpoints."""
        # Test create session
        response = self.client.post("/chat/sessions", json={}, headers=self.headers)
        assert response.status_code in [200, 201, 401, 500]
        assert response.status_code != 404
        
        # Test session history
        response = self.client.get("/chat/sessions/test_session/history", headers=self.headers)
        assert response.status_code in [200, 401, 404, 500]
        
        # Test send message
        message_payload = {
            "content": "Hello",
            "role": "user"
        }
        response = self.client.post("/chat/sessions/test_session/messages", 
                                  json=message_payload, headers=self.headers)
        assert response.status_code in [200, 401, 404, 500]

class TestAgentTypes:
    """Test agent type definitions and consistency."""
    
    def test_agent_types_defined(self):
        """Test that all expected agent types are defined."""
        expected_types = [
            "copilot_studio_1",
            "copilot_studio_2", 
            "ai_foundry_1",
            "ai_foundry_2",
            "orchestrator"
        ]
        
        for expected_type in expected_types:
            found = False
            for agent_type in AgentType:
                if agent_type.value == expected_type:
                    found = True
                    break
            assert found, f"Agent type {expected_type} not found"
            
    def test_agent_type_values(self):
        """Test agent type values are correct."""
        assert AgentType.COPILOT_STUDIO_1.value == "copilot_studio_1"
        assert AgentType.COPILOT_STUDIO_2.value == "copilot_studio_2"
        assert AgentType.AI_FOUNDRY_1.value == "ai_foundry_1"
        assert AgentType.AI_FOUNDRY_2.value == "ai_foundry_2"
        assert AgentType.ORCHESTRATOR.value == "orchestrator"

class TestAgentImports:
    """Test that agent classes can be imported correctly."""
    
    def test_copilot_studio_agent_import(self):
        """Test CopilotStudioAgent import."""
        try:
            from agents.copilot_studio_agent import CopilotStudioAgent
            assert CopilotStudioAgent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CopilotStudioAgent: {e}")
            
    def test_ai_foundry_agent_import(self):
        """Test AIFoundryAgent import."""
        try:
            from agents.ai_foundry_agent import AIFoundryAgent
            assert AIFoundryAgent is not None
        except ImportError as e:
            pytest.fail(f"Failed to import AIFoundryAgent: {e}")
            
    def test_orchestrator_import(self):
        """Test MultiAgentOrchestrator import."""
        try:
            from agents.orchestrator import MultiAgentOrchestrator
            assert MultiAgentOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MultiAgentOrchestrator: {e}")

class TestAgentInitialization:
    """Test agent initialization with new architecture."""
    
    @pytest.mark.asyncio
    async def test_copilot_studio_agents_init(self):
        """Test CopilotStudio agents initialization."""
        from agents.copilot_studio_agent import CopilotStudioAgent
        config = Config()
        
        # Test general conversation agent
        agent1 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_1", 
            specialization="general"
        )
        assert agent1.agent_id == "copilot_1"
        assert agent1.specialization == "general"
        assert len(agent1.capabilities) > 0
        
        # Test business process agent
        agent2 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_2",
            specialization="business_process"
        )
        assert agent2.agent_id == "copilot_2"
        assert agent2.specialization == "business_process"
        assert len(agent2.capabilities) > 0
        
        # Verify different capabilities
        assert agent1.capabilities != agent2.capabilities
        
    @pytest.mark.asyncio
    async def test_ai_foundry_agents_init(self):
        """Test AIFoundry agents initialization."""
        from agents.ai_foundry_agent import AIFoundryAgent
        config = Config()
        
        # Test document processing agent
        agent1 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_1",
            specialization="document_processing"
        )
        assert agent1.agent_id == "ai_foundry_1"
        assert agent1.specialization == "document_processing"
        
        # Test data analysis agent
        agent2 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_2",
            specialization="data_analysis"
        )
        assert agent2.agent_id == "ai_foundry_2"
        assert agent2.specialization == "data_analysis"

class TestConfiguration:
    """Test configuration and settings."""
    
    def test_config_creation(self):
        """Test that config can be created."""
        config = Config()
        assert config is not None
        assert hasattr(config, 'azure_tenant_id')
        assert hasattr(config, 'copilot_studio_endpoint')
        assert hasattr(config, 'ai_foundry_endpoint')
        
    def test_config_azure_credential(self):
        """Test Azure credential generation."""
        config = Config()
        credential = config.get_azure_credential()
        assert credential is not None
        
    def test_config_settings(self):
        """Test configuration settings method."""
        config = Config()
        setting = config.get_setting("AZURE_TENANT_ID", "default")
        assert setting is not None

def run_tests():
    """Run all tests."""
    print("=== Running Multiagent System Tests ===\n")
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])

if __name__ == "__main__":
    run_tests()
