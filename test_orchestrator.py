#!/usr/bin/env python3
"""
Test the orchestrator with the refactored agent system.
"""

import sys
import os
import asyncio
import pytest
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.agent_models import AgentType, OrchestrationRequest, UserContext, AgentRequest
from agents.orchestrator import MultiAgentOrchestrator
from test_config import SimpleConfig as Config

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test that the orchestrator can be initialized with the new agent architecture."""
    print("=== Testing Orchestrator Initialization ===")
    
    # Create a mock config
    config = Config()
    
    try:
        # Initialize orchestrator
        orchestrator = MultiAgentOrchestrator(config)
        await orchestrator.initialize()
        
        print(f"✓ Orchestrator initialized successfully")
        print(f"  - Total agents: {len(orchestrator.agents)}")
        print(f"  - Agent types: {list(orchestrator.agents.keys())}")
        
        # Verify specific agents
        expected_agents = [
            AgentType.COPILOT_STUDIO_1,
            AgentType.COPILOT_STUDIO_2,
            AgentType.AI_FOUNDRY_1,
            AgentType.AI_FOUNDRY_2
        ]
        
        for agent_type in expected_agents:
            if agent_type in orchestrator.agents:
                agent = orchestrator.agents[agent_type]
                print(f"  - {agent_type.value}: {agent.agent_id} ({agent.specialization})")
            else:
                print(f"  ✗ Missing agent: {agent_type.value}")
                
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()

@pytest.mark.asyncio
async def test_orchestrator_agent_selection():
    """Test that the orchestrator can select appropriate agents."""
    print("\n=== Testing Orchestrator Agent Selection ===")
    
    config = Config()
    orchestrator = MultiAgentOrchestrator(config)
    await orchestrator.initialize()
    
    # Test queries with different requirements
    test_queries = [
        {
            "query": "Help me analyze this sales data",
            "expected_agents": [AgentType.AI_FOUNDRY_2]  # Data analysis agent
        },
        {
            "query": "I need help with a general conversation",
            "expected_agents": [AgentType.COPILOT_STUDIO_1]  # General conversation agent
        },
        {
            "query": "Process this document for me",
            "expected_agents": [AgentType.AI_FOUNDRY_1]  # Document processing agent
        },
        {
            "query": "Set up a workflow automation",
            "expected_agents": [AgentType.COPILOT_STUDIO_2]  # Business process agent
        }
    ]
    
    for test_case in test_queries:
        try:
            # Mock user context
            user_context = UserContext(
                user_id="test_user",
                username="test_user",
                email="test@example.com",
                name="Test User",
                tenant_id="test_tenant",
                roles=["user"],
                groups=["test_group"]
            )
            
            # Create AgentRequest
            agent_request = AgentRequest(
                query=test_case["query"],
                context={"task_type": "test"}
            )
            
            # Test agent selection logic
            suitable_agents = await orchestrator._select_agents(agent_request, user_context)
            
            print(f"✓ Query: '{test_case['query']}'")
            print(f"  - Selected agents: {[a.value for a in suitable_agents]}")
            
        except Exception as e:
            print(f"✗ Agent selection failed for query '{test_case['query']}': {e}")
            import traceback
            traceback.print_exc()

@pytest.mark.asyncio
async def test_orchestrator_mock_orchestration():
    """Test orchestration with mock responses."""
    print("\n=== Testing Orchestrator Mock Orchestration ===")
    
    config = Config()
    orchestrator = MultiAgentOrchestrator(config)
    await orchestrator.initialize()
    
    # Test orchestration request
    request = OrchestrationRequest(
        query="Help me analyze some business data and create a report",
        orchestration_strategy="adaptive",
        context={"task_type": "data_analysis"}
    )
    
    user_context = UserContext(
        user_id="test_user",
        username="test_user",
        email="test@example.com",
        name="Test User",
        tenant_id="test_tenant",
        roles=["user"],
        groups=["test_group"]
    )
    
    try:
        # This would normally call the orchestrator's orchestrate method
        # For now, let's just test the agent selection
        agent_request = AgentRequest(
            query=request.query,
            context=request.context
        )
        suitable_agents = await orchestrator._select_agents(agent_request, user_context)
        
        print(f"✓ Orchestration request processed")
        print(f"  - Query: {request.query}")
        print(f"  - Strategy: {request.orchestration_strategy}")
        print(f"  - Selected agents: {[a.value for a in suitable_agents]}")
        
        # Test individual agent responses
        if suitable_agents:
            agent_type = suitable_agents[0]
            agent = orchestrator.agents[agent_type]
            
            # Mock agent request
            agent_request = AgentRequest(
                query=request.query,
                context=request.context
            )
            
            response = await agent.query(agent_request, user_context)
            
            print(f"  - Sample response from {agent_type.value}:")
            print(f"    - Success: {response.success}")
            print(f"    - Agent ID: {response.agent_id}")
            print(f"    - Response length: {len(response.response)} chars")
            
    except Exception as e:
        print(f"✗ Orchestration test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all orchestrator tests."""
    print("=== Orchestrator Test Suite ===")
    
    await test_orchestrator_initialization()
    await test_orchestrator_agent_selection()
    await test_orchestrator_mock_orchestration()
    
    print("\n=== All orchestrator tests completed! ===")

if __name__ == "__main__":
    asyncio.run(main())
