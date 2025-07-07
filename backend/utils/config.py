"""
Configuration management for the multiagent system.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import logging

logger = logging.getLogger(__name__)

class Config(BaseModel):
    """Configuration class for the multiagent system."""
    
    # Azure Configuration
    azure_tenant_id: str
    azure_client_id: str
    azure_resource_group: str
    azure_subscription_id: str
    
    # Key Vault Configuration
    key_vault_url: str
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-4o"
    
    # Azure AI Services Configuration
    azure_ai_services_endpoint: str
    azure_ai_services_api_version: str = "2024-02-01"
    
    # Copilot Studio Configuration
    copilot_studio_endpoint: str
    copilot_studio_bot_id: str
    
    # Azure AI Foundry Configuration
    ai_foundry_endpoint: str
    ai_foundry_workspace_id: str
    
    # Microsoft Graph Configuration
    microsoft_graph_endpoint: str = "https://graph.microsoft.com"
    microsoft_graph_scopes: list = ["https://graph.microsoft.com/.default"]
    
    # Application Insights Configuration
    application_insights_connection_string: str
    
    # LangChain Configuration
    langchain_project: str = "multiagent-demo"
    langchain_tracing_enabled: bool = False
    
    # Database Configuration
    cosmos_db_endpoint: str
    cosmos_db_database_name: str = "multiagent"
    cosmos_db_container_name: str = "sessions"
    
    # Redis Configuration (for caching)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # Security Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # RBAC Configuration
    rbac_enabled: bool = True
    default_user_permissions: Dict[str, Any] = {
        "copilot_studio": False,
        "ai_foundry": False
    }
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    
    # Logging Configuration
    log_level: str = "INFO"
    
    def __init__(self):
        """Initialize configuration from environment variables and Key Vault."""
        # Get basic configuration from environment
        self.azure_tenant_id = os.getenv("AZURE_TENANT_ID", "")
        self.azure_client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP", "")
        self.azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        
        self.key_vault_url = os.getenv("KEY_VAULT_URL", "")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.azure_ai_services_endpoint = os.getenv("AZURE_AI_SERVICES_ENDPOINT", "")
        self.application_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
        
        # Load additional configuration from Key Vault
        self._load_from_key_vault()
        
        # Load from environment variables with defaults
        self.copilot_studio_endpoint = os.getenv("COPILOT_STUDIO_ENDPOINT", "")
        self.copilot_studio_bot_id = os.getenv("COPILOT_STUDIO_BOT_ID", "")
        self.ai_foundry_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT", "")
        self.ai_foundry_workspace_id = os.getenv("AI_FOUNDRY_WORKSPACE_ID", "")
        self.cosmos_db_endpoint = os.getenv("COSMOS_DB_ENDPOINT", "")
        
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate required configuration
        self._validate_configuration()
    
    def _load_from_key_vault(self):
        """Load sensitive configuration from Azure Key Vault."""
        if not self.key_vault_url:
            logger.warning("Key Vault URL not configured, skipping Key Vault configuration")
            return
        
        try:
            # Initialize credential
            credential = DefaultAzureCredential()
            
            # Create Key Vault client
            kv_client = SecretClient(vault_url=self.key_vault_url, credential=credential)
            
            # Load secrets
            secrets_to_load = [
                "jwt-secret-key",
                "copilot-studio-endpoint",
                "copilot-studio-bot-id",
                "ai-foundry-endpoint",
                "ai-foundry-workspace-id",
                "cosmos-db-endpoint",
                "redis-password"
            ]
            
            for secret_name in secrets_to_load:
                try:
                    secret = kv_client.get_secret(secret_name)
                    attr_name = secret_name.replace("-", "_")
                    setattr(self, attr_name, secret.value)
                    logger.info(f"Loaded secret: {secret_name}")
                except Exception as e:
                    logger.warning(f"Failed to load secret {secret_name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from Key Vault: {str(e)}")
    
    def _validate_configuration(self):
        """Validate required configuration values."""
        required_fields = [
            "azure_tenant_id",
            "azure_client_id",
            "azure_openai_endpoint",
            "azure_ai_services_endpoint",
            "application_insights_connection_string"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field, None):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
    
    def get_azure_credential(self) -> DefaultAzureCredential:
        """Get Azure credential for authentication."""
        if self.azure_client_id:
            return ManagedIdentityCredential(client_id=self.azure_client_id)
        else:
            return DefaultAzureCredential()
    
    def get_openai_config(self) -> Dict[str, str]:
        """Get OpenAI configuration."""
        return {
            "azure_endpoint": self.azure_openai_endpoint,
            "api_version": self.azure_openai_api_version,
            "deployment_name": self.azure_openai_deployment_name
        }
    
    def get_ai_services_config(self) -> Dict[str, str]:
        """Get AI Services configuration."""
        return {
            "endpoint": self.azure_ai_services_endpoint,
            "api_version": self.azure_ai_services_api_version
        }
    
    def get_graph_config(self) -> Dict[str, Any]:
        """Get Microsoft Graph configuration."""
        return {
            "endpoint": self.microsoft_graph_endpoint,
            "scopes": self.microsoft_graph_scopes
        }
    
    def get_rbac_config(self) -> Dict[str, Any]:
        """Get RBAC configuration."""
        return {
            "enabled": self.rbac_enabled,
            "default_permissions": self.default_user_permissions
        }
    
    def get_rate_limit_config(self) -> Dict[str, int]:
        """Get rate limiting configuration."""
        return {
            "requests_per_minute": self.rate_limit_requests_per_minute,
            "requests_per_hour": self.rate_limit_requests_per_hour
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        config_dict = {}
        sensitive_fields = ["jwt_secret_key", "redis_password"]
        
        for key, value in self.__dict__.items():
            if key not in sensitive_fields:
                config_dict[key] = value
        
        return config_dict
