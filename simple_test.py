#!/usr/bin/env python3
"""
Simple test to verify agent types and basic functionality.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.agent_models import AgentType

def test_agent_types():
    """Test that all agent types are properly defined."""
    print("Testing agent types...")
    
    # Test that all expected agent types exist
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
    
    print("Agent types test completed!\n")

def test_agent_imports():
    """Test that agent classes can be imported."""
    print("Testing agent imports...")
    
    try:
        from agents.copilot_studio_agent import CopilotStudioAgent
        print("✓ CopilotStudioAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CopilotStudioAgent: {e}")
    
    try:
        from agents.ai_foundry_agent import AIFoundryAgent
        print("✓ AIFoundryAgent imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AIFoundryAgent: {e}")
    
    print("Agent imports test completed!\n")

def main():
    """Run all tests."""
    print("=== Simple Agent System Test ===\n")
    
    test_agent_types()
    test_agent_imports()
    
    print("=== Test completed! ===")

if __name__ == "__main__":
    main()
