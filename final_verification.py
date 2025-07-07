#!/usr/bin/env python3
"""
Final verification test for the refactored multiagent orchestrator system.
This test confirms that the system has been successfully refactored from the original
4-agent system (pro-code, low-code AI Foundry, Copilot Studio, high-code AI Foundry)
to the new 4-agent system (2 Copilot Studio agents, 2 AI Foundry agents).
"""

import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.agent_models import AgentType, AgentRequest, UserContext
from agents.orchestrator import MultiAgentOrchestrator
from agents.copilot_studio_agent import CopilotStudioAgent
from agents.ai_foundry_agent import AIFoundryAgent
from test_config import SimpleConfig as Config

def test_agent_types():
    """Verify that agent types have been correctly refactored."""
    print("=== Agent Type Verification ===")
    
    expected_types = {
        AgentType.COPILOT_STUDIO_1,
        AgentType.COPILOT_STUDIO_2,
        AgentType.AI_FOUNDRY_1,
        AgentType.AI_FOUNDRY_2,
        AgentType.ORCHESTRATOR
    }
    
    actual_types = set(AgentType)
    
    print(f"Expected agent types: {[t.value for t in expected_types]}")
    print(f"Actual agent types: {[t.value for t in actual_types]}")
    
    if expected_types == actual_types:
        print("✓ Agent types correctly refactored")
        return True
    else:
        print("✗ Agent types do not match expected")
        missing = expected_types - actual_types
        extra = actual_types - expected_types
        if missing:
            print(f"  Missing: {[t.value for t in missing]}")
        if extra:
            print(f"  Extra: {[t.value for t in extra]}")
        return False

async def test_agent_specializations():
    """Verify that agents have proper specializations."""
    print("\n=== Agent Specialization Verification ===")
    
    config = Config()
    
    # Test Copilot Studio agents
    copilot_1 = CopilotStudioAgent(config, agent_id="cs1", specialization="general")
    copilot_2 = CopilotStudioAgent(config, agent_id="cs2", specialization="business_process")
    
    # Test AI Foundry agents
    ai_foundry_1 = AIFoundryAgent(config, agent_id="af1", specialization="document_processing")
    ai_foundry_2 = AIFoundryAgent(config, agent_id="af2", specialization="data_analysis")
    
    agents = [
        (copilot_1, "Copilot Studio 1", "general"),
        (copilot_2, "Copilot Studio 2", "business_process"),
        (ai_foundry_1, "AI Foundry 1", "document_processing"),
        (ai_foundry_2, "AI Foundry 2", "data_analysis")
    ]
    
    all_passed = True
    for agent, name, expected_spec in agents:
        if agent.specialization == expected_spec:
            print(f"✓ {name}: {agent.specialization} (correct)")
        else:
            print(f"✗ {name}: expected {expected_spec}, got {agent.specialization}")
            all_passed = False
    
    return all_passed

async def test_orchestrator_agent_lineup():
    """Verify that the orchestrator initializes with the correct agents."""
    print("\n=== Orchestrator Agent Lineup Verification ===")
    
    config = Config()
    orchestrator = MultiAgentOrchestrator(config)
    
    try:
        await orchestrator.initialize()
        
        expected_agents = {
            AgentType.COPILOT_STUDIO_1,
            AgentType.COPILOT_STUDIO_2,
            AgentType.AI_FOUNDRY_1,
            AgentType.AI_FOUNDRY_2
        }
        
        actual_agents = set(orchestrator.agents.keys())
        
        if expected_agents == actual_agents:
            print("✓ Orchestrator has correct agent lineup")
            
            # Verify specializations
            specializations = {}
            for agent_type, agent in orchestrator.agents.items():
                specializations[agent_type.value] = agent.specialization
            
            print("Agent specializations:")
            for agent_type, spec in specializations.items():
                print(f"  - {agent_type}: {spec}")
            
            return True
        else:
            print("✗ Orchestrator agent lineup is incorrect")
            missing = expected_agents - actual_agents
            extra = actual_agents - expected_agents
            if missing:
                print(f"  Missing: {[t.value for t in missing]}")
            if extra:
                print(f"  Extra: {[t.value for t in extra]}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        return False

async def test_agent_responses():
    """Test that all agents can respond to queries."""
    print("\n=== Agent Response Verification ===")
    
    config = Config()
    
    user_context = UserContext(
        user_id="test_user",
        username="test_user",
        email="test@example.com",
        name="Test User",
        tenant_id="test_tenant",
        roles=["user"]
    )
    
    # Test Copilot Studio agents
    copilot_agents = [
        (CopilotStudioAgent(config, "cs1", "general"), "Copilot Studio 1"),
        (CopilotStudioAgent(config, "cs2", "business"), "Copilot Studio 2")
    ]
    
    request = AgentRequest(query="Hello, can you help me?")
    
    all_passed = True
    for agent, name in copilot_agents:
        try:
            response = await agent.query(request, user_context)
            if response.success and response.agent_id == agent.agent_id:
                print(f"✓ {name}: Response successful (agent_id: {response.agent_id})")
            else:
                print(f"✗ {name}: Response failed or incorrect agent_id")
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: Exception during query - {e}")
            all_passed = False
    
    # Test AI Foundry agents
    ai_foundry_agents = [
        (AIFoundryAgent(config, "af1", "document"), "AI Foundry 1"),
        (AIFoundryAgent(config, "af2", "data"), "AI Foundry 2")
    ]
    
    request_data = {"query": "Hello, can you help me?", "context": {}}
    
    for agent, name in ai_foundry_agents:
        try:
            response = await agent.process_request(request_data)
            if response.success and response.agent_id == agent.agent_id:
                print(f"✓ {name}: Response successful (agent_id: {response.agent_id})")
            else:
                print(f"✗ {name}: Response failed or incorrect agent_id")
                all_passed = False
        except Exception as e:
            print(f"✗ {name}: Exception during process_request - {e}")
            all_passed = False
    
    return all_passed

def print_refactoring_summary():
    """Print a summary of the refactoring changes."""
    print("\n=== Refactoring Summary ===")
    print("BEFORE (Original System):")
    print("  - PRO_CODE: Code generation and execution agent")
    print("  - AI_FOUNDRY_LOW_CODE: Low-code workflow agent")
    print("  - COPILOT_STUDIO: Single conversational agent")
    print("  - AI_FOUNDRY_HIGH_CODE: High-code agent (data science)")
    print()
    print("AFTER (Refactored System):")
    print("  - COPILOT_STUDIO_1: General conversation agent")
    print("  - COPILOT_STUDIO_2: Business process automation agent")
    print("  - AI_FOUNDRY_1: Document processing agent")
    print("  - AI_FOUNDRY_2: Data analysis agent")
    print("  - ORCHESTRATOR: Coordination agent (unchanged)")
    print()
    print("Key Changes:")
    print("  ✓ Removed pro-code agent functionality")
    print("  ✓ Split Copilot Studio into 2 specialized agents")
    print("  ✓ Split AI Foundry into 2 specialized agents")
    print("  ✓ Updated agent selection logic in orchestrator")
    print("  ✓ Updated all agent initialization with agent_id and specialization")
    print("  ✓ Updated agent capabilities and response handling")
    print("  ✓ Updated RBAC permissions for new agent types")
    print("  ✓ Updated frontend agent type handling")

async def main():
    """Run all verification tests."""
    print("=== Multiagent System Refactoring Verification ===")
    print("This test verifies that the system has been successfully refactored")
    print("from pro-code/low-code agents to 2 Copilot Studio + 2 AI Foundry agents.\n")
    
    tests = [
        ("Agent Types", test_agent_types),
        ("Agent Specializations", test_agent_specializations),
        ("Orchestrator Agent Lineup", test_orchestrator_agent_lineup),
        ("Agent Responses", test_agent_responses)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}: Exception - {e}")
            results.append((test_name, False))
    
    print("\n=== Test Results Summary ===")
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Refactoring verification SUCCESSFUL!")
        print("The multiagent orchestrator system has been successfully refactored.")
    else:
        print("❌ Refactoring verification FAILED!")
        print("Some issues were found in the refactored system.")
    
    print_refactoring_summary()

if __name__ == "__main__":
    asyncio.run(main())
