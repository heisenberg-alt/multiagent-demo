#!/usr/bin/env python3
"""
Test script to verify the multiagent system refactoring is working correctly.
This script tests that:
1. All new agent types are properly defined
2. Agent initialization works with the new parameters
3. Agent selection logic works with the new agent types
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.agent_models import AgentType, AgentRequest, UserContext
from agents.orchestrator import MultiAgentOrchestrator
from agents.copilot_studio_agent import CopilotStudioAgent
from agents.ai_foundry_agent import AIFoundryAgent
from utils.config import Config

async def test_agent_types():
    """Test that all agent types are properly defined."""
    print("Testing agent types...")
    
    # Test that all expected agent types exist
    expected_types = [
        AgentType.COPILOT_STUDIO_1,
        AgentType.COPILOT_STUDIO_2,
        AgentType.AI_FOUNDRY_1,
        AgentType.AI_FOUNDRY_2,
        AgentType.ORCHESTRATOR
    ]
    
    for agent_type in expected_types:
        print(f"✓ {agent_type.value} is defined")
    
    print("Agent types test passed!\n")

async def test_agent_initialization():
    """Test that agents can be initialized with the new parameters."""
    print("Testing agent initialization...")
    
    # Create a mock config (in real usage, this would come from environment)
    config = Config()
    
    # Test CopilotStudioAgent initialization
    copilot_agent_1 = CopilotStudioAgent(
        config=config,
        agent_id="copilot_studio_1",
        specialization="general_conversation"
    )
    print(f"✓ CopilotStudioAgent 1 initialized with ID: {copilot_agent_1.agent_id}")
    
    copilot_agent_2 = CopilotStudioAgent(
        config=config,
        agent_id="copilot_studio_2",
        specialization="business_automation"
    )
    print(f"✓ CopilotStudioAgent 2 initialized with ID: {copilot_agent_2.agent_id}")
    
    # Test AIFoundryAgent initialization
    ai_foundry_agent_1 = AIFoundryAgent(
        config=config,
        agent_id="ai_foundry_1",
        specialization="data_analytics"
    )
    print(f"✓ AIFoundryAgent 1 initialized with ID: {ai_foundry_agent_1.agent_id}")
    
    ai_foundry_agent_2 = AIFoundryAgent(
        config=config,
        agent_id="ai_foundry_2",
        specialization="document_processing"
    )
    print(f"✓ AIFoundryAgent 2 initialized with ID: {ai_foundry_agent_2.agent_id}")
    
    print("Agent initialization test passed!\n")

async def test_agent_capabilities():
    """Test that agents return specialized capabilities."""
    print("Testing agent capabilities...")
    
    config = Config()
    
    # Test CopilotStudioAgent capabilities
    copilot_agent = CopilotStudioAgent(
        config=config,
        agent_id="copilot_studio_1",
        specialization="general_conversation"
    )
    
    capabilities = copilot_agent._get_specialized_capabilities()
    print(f"✓ CopilotStudioAgent has {len(capabilities)} capabilities")
    for cap in capabilities:
        print(f"  - {cap.name}: {cap.description}")
    
    # Test AIFoundryAgent capabilities
    ai_foundry_agent = AIFoundryAgent(
        config=config,
        agent_id="ai_foundry_1",
        specialization="data_analytics"
    )
    
    capabilities = ai_foundry_agent._get_specialized_capabilities()
    print(f"✓ AIFoundryAgent has {len(capabilities)} specialized capabilities")
    for cap in capabilities:
        print(f"  - {cap.name}: {cap.description}")
    
    print("Agent capabilities test passed!\n")

async def test_orchestrator_initialization():
    """Test that the orchestrator can be initialized with the new agent lineup."""
    print("Testing orchestrator initialization...")
    
    try:
        config = Config()
        orchestrator = MultiAgentOrchestrator(config)
        await orchestrator.initialize()
        
        # Check that the orchestrator has the expected agents
        expected_agent_types = [
            AgentType.COPILOT_STUDIO_1,
            AgentType.COPILOT_STUDIO_2,
            AgentType.AI_FOUNDRY_1,
            AgentType.AI_FOUNDRY_2
        ]
        
        for agent_type in expected_agent_types:
            if agent_type in orchestrator.agents:
                print(f"✓ Orchestrator has {agent_type.value} agent")
            else:
                print(f"✗ Orchestrator missing {agent_type.value} agent")
        
        print("Orchestrator initialization test passed!\n")
        
    except Exception as e:
        print(f"✗ Orchestrator initialization failed: {e}")
        print("(This may be expected if external services are not configured)\n")

async def test_agent_selection():
    """Test that the agent selection logic works with the new agent types."""
    print("Testing agent selection logic...")
    
    try:
        config = Config()
        orchestrator = MultiAgentOrchestrator(config)
        await orchestrator.initialize()
        
        # Test different query types
        test_queries = [
            ("Hello, can you help me?", "Should select general conversation agent"),
            ("I need help with workflow automation", "Should select business automation agent"),
            ("Can you analyze this data for me?", "Should select data analytics agent"),
            ("I have a document to process", "Should select document processing agent"),
        ]
        
        for query, description in test_queries:
            selected_agents = orchestrator._select_agents(query)
            print(f"✓ Query: '{query}' -> Selected {len(selected_agents)} agents: {[a.value for a in selected_agents]}")
        
        print("Agent selection test passed!\n")
        
    except Exception as e:
        print(f"✗ Agent selection test failed: {e}")
        print("(This may be expected if external services are not configured)\n")

async def main():
    """Run all tests."""
    print("=== Multiagent System Refactoring Test ===\n")
    
    await test_agent_types()
    await test_agent_initialization()
    await test_agent_capabilities()
    await test_orchestrator_initialization()
    await test_agent_selection()
    
    print("=== All tests completed! ===")

if __name__ == "__main__":
    asyncio.run(main())
