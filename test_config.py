#!/usr/bin/env python3
"""
Simple test configuration for testing without full environment setup.
"""
import os

class SimpleConfig:
    """Simple configuration class for testing."""
    
    def __init__(self):
        """Initialize simple configuration."""
        # Basic settings with defaults for testing
        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID", "test-tenant")
        self.azure_client_id = os.getenv("AZURE_CLIENT_ID", "test-client")
        self.azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP", "test-rg")
        self.azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "test-sub")
        
        # Service endpoints
        self.copilot_studio_endpoint = os.getenv("COPILOT_STUDIO_ENDPOINT", "")
        self.copilot_studio_bot_id = os.getenv("COPILOT_STUDIO_BOT_ID", "test-bot")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        self.azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.azure_ai_services_endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT", "")
        self.ai_foundry_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT", "")
        self.ai_foundry_api_key = os.getenv("AI_FOUNDRY_API_KEY", "")
        self.ai_foundry_deployment_name = os.getenv("AI_FOUNDRY_DEPLOYMENT_NAME", "gpt-4")
        
        # Logging and telemetry
        self.application_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
        self.log_level = "INFO"
        
        # RBAC settings
        self.rbac_enabled = True
        self.default_user_permissions = {
            "copilot_studio": True,
            "ai_foundry": True
        }
        
    def get_azure_credential(self):
        """Get Azure credential (mock for testing)."""
        from azure.identity import DefaultAzureCredential
        return DefaultAzureCredential()
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a configuration setting."""
        return getattr(self, key.lower(), default)
