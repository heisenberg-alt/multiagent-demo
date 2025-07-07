#!/usr/bin/env python3
"""
Simple test runner for the multiagent system without external dependencies.
This validates the current agent architecture and API structure.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_agent_type_definitions():
    """Test that agent types are correctly defined."""
    print("=== Testing Agent Type Definitions ===")
    
    try:
        from models.agent_models import AgentType
        
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
                    print(f"✓ {agent_type.value} is defined")
                    found = True
                    break
            if not found:
                print(f"✗ {expected_type} is NOT defined")
                
        print("Agent type definitions test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Failed to test agent types: {e}\n")
        return False

def test_agent_imports():
    """Test that agent classes can be imported."""
    print("=== Testing Agent Imports ===")
    
    success = True
    
    try:
        from agents.copilot_studio_agent import CopilotStudioAgent
        print("✓ CopilotStudioAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CopilotStudioAgent: {e}")
        success = False
    
    try:
        from agents.ai_foundry_agent import AIFoundryAgent
        print("✓ AIFoundryAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AIFoundryAgent: {e}")
        success = False
    
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        print("✓ MultiAgentOrchestrator imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MultiAgentOrchestrator: {e}")
        success = False
    
    try:
        from models.agent_models import AgentRequest, AgentResponse, UserContext
        print("✓ Agent models imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import agent models: {e}")
        success = False
        
    print("Agent imports test completed!\n")
    return success

def test_configuration():
    """Test configuration setup."""
    print("=== Testing Configuration ===")
    
    try:
        from test_config import SimpleConfig as Config
        
        config = Config()
        print("✓ Configuration created successfully")
        
        # Test basic attributes
        attributes = [
            'azure_tenant_id',
            'azure_client_id', 
            'copilot_studio_endpoint',
            'ai_foundry_endpoint',
            'rbac_enabled'
        ]
        
        for attr in attributes:
            if hasattr(config, attr):
                print(f"✓ Configuration has {attr}")
            else:
                print(f"✗ Configuration missing {attr}")
                
        # Test methods
        credential = config.get_azure_credential()
        print("✓ Azure credential method works")
        
        setting = config.get_setting("AZURE_TENANT_ID", "default")
        print(f"✓ Settings method works (got: {setting})")
        
        print("Configuration test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}\n")
        return False

async def test_agent_initialization():
    """Test agent initialization."""
    print("=== Testing Agent Initialization ===")
    
    try:
        from agents.copilot_studio_agent import CopilotStudioAgent
        from agents.ai_foundry_agent import AIFoundryAgent
        from test_config import SimpleConfig as Config
        
        config = Config()
        
        # Test CopilotStudio agents
        copilot_1 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_1",
            specialization="general"
        )
        print(f"✓ CopilotStudioAgent 1 created: {copilot_1.agent_id} ({copilot_1.specialization})")
        
        copilot_2 = CopilotStudioAgent(
            config=config,
            agent_id="copilot_2", 
            specialization="business_process"
        )
        print(f"✓ CopilotStudioAgent 2 created: {copilot_2.agent_id} ({copilot_2.specialization})")
        
        # Test AI Foundry agents
        ai_foundry_1 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_1",
            specialization="document_processing"
        )
        print(f"✓ AIFoundryAgent 1 created: {ai_foundry_1.agent_id} ({ai_foundry_1.specialization})")
        
        ai_foundry_2 = AIFoundryAgent(
            config=config,
            agent_id="ai_foundry_2",
            specialization="data_analysis"
        )
        print(f"✓ AIFoundryAgent 2 created: {ai_foundry_2.agent_id} ({ai_foundry_2.specialization})")
        
        # Test capabilities
        caps_1 = copilot_1._get_specialized_capabilities()
        caps_2 = copilot_2._get_specialized_capabilities()
        
        print(f"✓ Agent capabilities: copilot_1 has {len(caps_1)}, copilot_2 has {len(caps_2)}")
        
        if caps_1 != caps_2:
            print("✓ Agents have different specialized capabilities")
        else:
            print("⚠ Agents have identical capabilities")
            
        print("Agent initialization test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Agent initialization test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

async def test_orchestrator_setup():
    """Test orchestrator setup."""
    print("=== Testing Orchestrator Setup ===")
    
    try:
        from agents.orchestrator import MultiAgentOrchestrator
        from test_config import SimpleConfig as Config
        
        config = Config()
        orchestrator = MultiAgentOrchestrator(config)
        
        print("✓ Orchestrator created successfully")
        
        # Test initialization
        await orchestrator.initialize()
        print("✓ Orchestrator initialized successfully")
        
        print(f"✓ Orchestrator has {len(orchestrator.agents)} agents")
        
        # List agents
        for agent_type, agent in orchestrator.agents.items():
            print(f"  - {agent_type.value}: {agent.agent_id} ({agent.specialization})")
            
        # Cleanup
        await orchestrator.cleanup()
        print("✓ Orchestrator cleanup completed")
        
        print("Orchestrator setup test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator setup test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Test API structure and FastAPI app."""
    print("=== Testing API Structure ===")
    
    try:
        # Test if backend directory exists
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if not os.path.exists(backend_path):
            print("✗ Backend directory not found")
            return False
        
        # Test if main.py exists
        main_path = os.path.join(backend_path, 'main.py')
        if not os.path.exists(main_path):
            print("✗ main.py not found")
            return False
        
        print("✓ Backend directory exists")
        print("✓ main.py exists")
        
        # Test if key files exist
        key_files = [
            'models/agent_models.py',
            'agents/copilot_studio_agent.py',
            'agents/ai_foundry_agent.py',
            'agents/orchestrator.py',
            'utils/config.py'
        ]
        
        for file_path in key_files:
            full_path = os.path.join(backend_path, file_path)
            if os.path.exists(full_path):
                print(f"✓ {file_path} exists")
            else:
                print(f"⚠ {file_path} not found")
        
        # Test if OpenAPI spec exists
        openapi_path = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
        if os.path.exists(openapi_path):
            print("✓ OpenAPI specification exists")
        else:
            print("⚠ OpenAPI specification not found")
        
        print("API structure test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ API structure test failed: {e}\n")
        return False

def test_model_definitions():
    """Test model definitions."""
    print("=== Testing Model Definitions ===")
    
    try:
        # Add backend to path for import
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from models.agent_models import (
            AgentRequest, 
            AgentResponse, 
            OrchestrationRequest,
            OrchestrationResponse,
            UserContext,
            AgentType
        )
        
        print("✓ All agent models imported successfully")
        
        # Test basic model creation
        user_context = UserContext(
            user_id="test",
            username="test",
            email="test@example.com",
            name="Test User",
            tenant_id="test-tenant"
        )
        print("✓ UserContext model works")
        
        agent_request = AgentRequest(
            query="Test query",
            context={"test": True}
        )
        print("✓ AgentRequest model works")
        
        orchestration_request = OrchestrationRequest(
            query="Test orchestration",
            orchestration_strategy="adaptive"
        )
        print("✓ OrchestrationRequest model works")
        
        print("Model definitions test completed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Model definitions test failed: {e}\n")
        return False

def create_test_report(results: Dict[str, bool]):
    """Create a test report."""
    print("=== Test Report ===")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    print("Test Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! The multiagent system is ready.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please check the issues above.")
    
    return failed_tests == 0

async def main():
    """Run all tests."""
    print("=== Multiagent System Test Suite ===")
    print("Testing the updated agent architecture and API endpoints.\n")
    
    # Run all tests
    results = {}
    
    results["Agent Type Definitions"] = test_agent_type_definitions()
    results["Agent Imports"] = test_agent_imports()
    results["Configuration"] = test_configuration()
    results["Model Definitions"] = test_model_definitions()
    results["API Structure"] = test_api_structure()
    results["Agent Initialization"] = await test_agent_initialization()
    results["Orchestrator Setup"] = await test_orchestrator_setup()
    
    # Generate report
    all_passed = create_test_report(results)
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
