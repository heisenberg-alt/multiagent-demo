#!/usr/bin/env python3
"""
Comprehensive test to verify the multiagent system functionality.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.agent_models import AgentType, AgentRequest, UserContext
from agents.copilot_studio_agent import CopilotStudioAgent
from agents.ai_foundry_agent import AIFoundryAgent
from test_config import SimpleConfig as Config

async def test_agent_initialization():
    """Test that agents can be initialized with the new parameters."""
    print("=== Testing Agent Initialization ===")
    
    # Create a mock config
    config = Config()
    
    # Test CopilotStudioAgent initialization
    try:
        copilot_agent_1 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_1",
            specialization="general"
        )
        print(f"✓ CopilotStudioAgent 1 initialized")
        print(f"  - Agent ID: {copilot_agent_1.agent_id}")
        print(f"  - Specialization: {copilot_agent_1.specialization}")
        print(f"  - Capabilities: {len(copilot_agent_1.capabilities)} items")
        
        copilot_agent_2 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_2",
            specialization="business_process"
        )
        print(f"✓ CopilotStudioAgent 2 initialized")
        print(f"  - Agent ID: {copilot_agent_2.agent_id}")
        print(f"  - Specialization: {copilot_agent_2.specialization}")
        print(f"  - Capabilities: {len(copilot_agent_2.capabilities)} items")
        
    except Exception as e:
        print(f"✗ Failed to initialize CopilotStudioAgent: {e}")
    
    # Test AIFoundryAgent initialization
    try:
        ai_foundry_agent_1 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_1",
            specialization="document_processing"
        )
        print(f"✓ AIFoundryAgent 1 initialized")
        print(f"  - Agent ID: {ai_foundry_agent_1.agent_id}")
        print(f"  - Specialization: {ai_foundry_agent_1.specialization}")
        
        ai_foundry_agent_2 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_2",
            specialization="data_analysis"
        )
        print(f"✓ AIFoundryAgent 2 initialized")
        print(f"  - Agent ID: {ai_foundry_agent_2.agent_id}")
        print(f"  - Specialization: {ai_foundry_agent_2.specialization}")
        
    except Exception as e:
        print(f"✗ Failed to initialize AIFoundryAgent: {e}")
    
    print()

async def test_agent_capabilities():
    """Test that agents return specialized capabilities."""
    print("=== Testing Agent Capabilities ===")
    
    config = Config()
    
    # Test CopilotStudioAgent capabilities
    try:
        copilot_agent = CopilotStudioAgent(
            config=config,
            agent_id="copilot_1",
            specialization="general"
        )
        
        capabilities = copilot_agent._get_specialized_capabilities()
        print(f"✓ CopilotStudioAgent (general) has {len(capabilities)} capabilities:")
        for cap in capabilities:
            print(f"  - {cap}")
        
        business_agent = CopilotStudioAgent(
            config=config,
            agent_id="copilot_2",
            specialization="business_process"
        )
        
        business_capabilities = business_agent._get_specialized_capabilities()
        print(f"✓ CopilotStudioAgent (business) has {len(business_capabilities)} capabilities:")
        for cap in business_capabilities:
            print(f"  - {cap}")
        
    except Exception as e:
        print(f"✗ Failed to get CopilotStudioAgent capabilities: {e}")
    
    # Test AIFoundryAgent capabilities
    try:
        ai_foundry_agent = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_1",
            specialization="document_processing"
        )
        
        capabilities = ai_foundry_agent._get_specialized_capabilities()
        print(f"✓ AIFoundryAgent (document_processing) has {len(capabilities)} capabilities:")
        for cap in capabilities:
            print(f"  - {cap.name}: {cap.description}")
        
        data_agent = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_2",
            specialization="data_analysis"
        )
        
        data_capabilities = data_agent._get_specialized_capabilities()
        print(f"✓ AIFoundryAgent (data_analysis) has {len(data_capabilities)} capabilities:")
        for cap in data_capabilities:
            print(f"  - {cap.name}: {cap.description}")
        
    except Exception as e:
        print(f"✗ Failed to get AIFoundryAgent capabilities: {e}")
    
    print()

async def test_agent_responses():
    """Test that agents can generate responses."""
    print("=== Testing Agent Mock Responses ===")
    
    config = Config()
    
    # Create test user context
    user_context = UserContext(
        user_id="test_user",
        username="testuser",
        email="test@example.com",
        name="Test User",
        tenant_id="test_tenant",
        roles=["user"]
    )
    
    # Test CopilotStudioAgent response
    try:
        copilot_agent = CopilotStudioAgent(
            config=config,
            agent_id="copilot_1",
            specialization="general"
        )
        
        # Initialize the agent
        await copilot_agent.initialize()
        
        # Create a test request
        request = AgentRequest(
            query="Hello, can you help me with general questions?",
            session_id="test_session"
        )
        
        # Get response (this will use mock response since no real endpoint)
        response = await copilot_agent.query(request, user_context)
        
        print(f"✓ CopilotStudioAgent response:")
        print(f"  - Success: {response.success}")
        print(f"  - Agent Type: {response.agent_type}")
        print(f"  - Agent ID: {response.agent_id}")
        print(f"  - Response: {response.response[:100]}...")
        print(f"  - Confidence: {response.confidence}")
        print(f"  - Execution Time: {response.execution_time}s")
        
        # Cleanup
        await copilot_agent.cleanup()
        
    except Exception as e:
        print(f"✗ Failed to get CopilotStudioAgent response: {e}")
    
    # Test AIFoundryAgent response
    try:
        ai_foundry_agent = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_1",
            specialization="document_processing"
        )
        
        # Initialize the agent
        await ai_foundry_agent.initialize()
        
        # Create a test request for document processing
        # Create a test request for document processing
        request = AgentRequest(
            query="Process this document for key information extraction",
            context={"document_type": "contract"}
        )
        
        # Get response (this will use mock response)
        response = await ai_foundry_agent.query(request, user_context)
        
        print(f"✓ AIFoundryAgent response:")
        print(f"  - Success: {response.success}")
        print(f"  - Agent Type: {response.agent_type}")
        print(f"  - Agent ID: {response.agent_id}")
        print(f"  - Response: {response.response[:100]}...")
        print(f"  - Confidence: {response.confidence}")
        print(f"  - Execution Time: {response.execution_time}s")
        
        # Cleanup
        await ai_foundry_agent.cleanup()
        
    except Exception as e:
        print(f"✗ Failed to get AIFoundryAgent response: {e}")
    
    print()

async def test_agent_type_mapping():
    """Test that agent types are correctly mapped."""
    print("=== Testing Agent Type Mapping ===")
    
    config = Config()
    
    # Test that agents return correct agent types based on their IDs
    test_cases = [
        ("copilot_1", "general", AgentType.COPILOT_STUDIO_1),
        ("copilot_2", "business_process", AgentType.COPILOT_STUDIO_2),
        ("ai_foundry_1", "document_processing", AgentType.AI_FOUNDRY_1),
        ("ai_foundry_2", "data_analysis", AgentType.AI_FOUNDRY_2),
    ]
    
    for agent_id, specialization, expected_type in test_cases:
        try:
            if "copilot" in agent_id:
                agent = CopilotStudioAgent(config, agent_id, specialization)
                await agent.initialize()
                
                request = AgentRequest(
                    query="Test query",
                    session_id="test_session"
                )
                user_context = UserContext(
                    user_id="test_user",
                    username="testuser",
                    email="test@example.com",
                    name="Test User",
                    tenant_id="test_tenant",
                    roles=["user"]
                )
                
                response = await agent.query(request, user_context)
                actual_type = response.agent_type
                
                await agent.cleanup()
                
            else:  # ai_foundry
                agent = AIFoundryAgent(config, agent_id, specialization)
                await agent.initialize()
                
                request = AgentRequest(
                    query="Test query",
                    context={"test": True}
                )
                response = await agent.query(request, user_context)
                actual_type = response.agent_type
                
                await agent.cleanup()
            
            if actual_type == expected_type:
                print(f"✓ {agent_id} correctly returns {expected_type.value}")
            else:
                print(f"✗ {agent_id} returns {actual_type.value}, expected {expected_type.value}")
                
        except Exception as e:
            print(f"✗ Failed to test {agent_id}: {e}")
    
    print()

async def main():
    """Run all tests."""
    print("=== Comprehensive Multiagent System Test ===\n")
    
    await test_agent_initialization()
    await test_agent_capabilities()
    await test_agent_responses()
    await test_agent_type_mapping()
    
    print("=== All tests completed! ===")

if __name__ == "__main__":
    asyncio.run(main())
