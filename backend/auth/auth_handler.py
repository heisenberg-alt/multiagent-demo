"""
Authentication handler for Azure AD/Entra ID integration.
"""

import logging
from typing import Optional, Dict, Any
import jwt
import httpx
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
import msal
import json

from utils.config import Config
from models.agent_models import UserContext

logger = logging.getLogger(__name__)

class AuthHandler:
    """Handles authentication with Azure AD/Entra ID."""
    
    def __init__(self, config: Config):
        """Initialize authentication handler."""
        self.config = config
        self.tenant_id = config.azure_tenant_id
        self.client_id = config.azure_client_id
        self.jwt_secret = config.jwt_secret_key
        self.jwt_algorithm = config.jwt_algorithm
        self.jwt_expiration = config.jwt_expiration_minutes
        
        # Microsoft Graph configuration
        self.graph_endpoint = config.microsoft_graph_endpoint
        self.graph_scopes = config.microsoft_graph_scopes
        
        # Initialize MSAL client for server-side operations
        self.msal_app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=None  # Using managed identity
        )
        
        # Azure credential for accessing Graph API
        self.credential = config.get_azure_credential()
        
        logger.info("Authentication handler initialized")
    
    async def validate_token(self, token: str) -> UserContext:
        """Validate an access token and return user context."""
        try:
            # First try to validate as Azure AD token
            user_context = await self._validate_azure_ad_token(token)
            if user_context:
                return user_context
            
            # If not Azure AD token, try JWT token
            return self._validate_jwt_token(token)
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise ValueError("Invalid token")
    
    async def _validate_azure_ad_token(self, token: str) -> Optional[UserContext]:
        """Validate Azure AD access token."""
        try:
            # Get Azure AD public keys
            jwks_url = f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                jwks = response.json()
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            # Find the matching key
            key = None
            for jwk in jwks['keys']:
                if jwk['kid'] == kid:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                    break
            
            if not key:
                return None
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
            )
            
            # Extract user information
            user_context = UserContext(
                user_id=payload.get('oid', payload.get('sub')),
                username=payload.get('preferred_username', payload.get('unique_name')),
                email=payload.get('email', payload.get('upn')),
                name=payload.get('name', ''),
                tenant_id=payload.get('tid', self.tenant_id),
                roles=payload.get('roles', []),
                groups=payload.get('groups', []),
                app_roles=payload.get('app_roles', {}),
                token_type='azure_ad',
                expires_at=datetime.fromtimestamp(payload.get('exp', 0))
            )
            
            # Enrich with additional user information from Graph API
            await self._enrich_user_context(user_context, token)
            
            return user_context
            
        except jwt.ExpiredSignatureError:
            logger.warning("Azure AD token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid Azure AD token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Azure AD token validation error: {str(e)}")
            return None
    
    def _validate_jwt_token(self, token: str) -> UserContext:
        """Validate custom JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            user_context = UserContext(
                user_id=payload['user_id'],
                username=payload.get('username', ''),
                email=payload.get('email', ''),
                name=payload.get('name', ''),
                tenant_id=payload.get('tenant_id', self.tenant_id),
                roles=payload.get('roles', []),
                groups=payload.get('groups', []),
                app_roles=payload.get('app_roles', {}),
                token_type='jwt',
                expires_at=datetime.fromtimestamp(payload['exp'])
            )
            
            return user_context
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise ValueError("Invalid token")
    
    async def _enrich_user_context(self, user_context: UserContext, token: str):
        """Enrich user context with additional information from Microsoft Graph."""
        try:
            # Get user profile from Microsoft Graph
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                # Get user profile
                response = await client.get(
                    f"{self.graph_endpoint}/v1.0/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    profile = response.json()
                    
                    # Update user context with profile information
                    if not user_context.email:
                        user_context.email = profile.get('mail', profile.get('userPrincipalName', ''))
                    if not user_context.name:
                        user_context.name = profile.get('displayName', '')
                    
                    # Add additional profile data
                    user_context.profile = {
                        'job_title': profile.get('jobTitle', ''),
                        'department': profile.get('department', ''),
                        'office_location': profile.get('officeLocation', ''),
                        'phone': profile.get('businessPhones', []),
                        'manager': profile.get('manager', {})
                    }
                
                # Get user's group memberships
                response = await client.get(
                    f"{self.graph_endpoint}/v1.0/me/memberOf",
                    headers=headers
                )
                
                if response.status_code == 200:
                    memberships = response.json()
                    user_context.groups = [
                        group['id'] for group in memberships.get('value', [])
                        if group.get('@odata.type') == '#microsoft.graph.group'
                    ]
                
        except Exception as e:
            logger.warning(f"Failed to enrich user context: {str(e)}")
    
    def create_jwt_token(self, user_context: UserContext) -> str:
        """Create a JWT token for a user."""
        payload = {
            'user_id': user_context.user_id,
            'username': user_context.username,
            'email': user_context.email,
            'name': user_context.name,
            'tenant_id': user_context.tenant_id,
            'roles': user_context.roles,
            'groups': user_context.groups,
            'app_roles': user_context.app_roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=self.jwt_expiration)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh an access token using a refresh token."""
        try:
            # This would typically involve calling the Azure AD token endpoint
            # For simplicity, we'll just validate the refresh token and create a new one
            # In production, you should implement proper refresh token flow
            
            # Decode refresh token to get user info
            payload = jwt.decode(
                refresh_token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # Create new user context
            user_context = UserContext(
                user_id=payload['user_id'],
                username=payload.get('username', ''),
                email=payload.get('email', ''),
                name=payload.get('name', ''),
                tenant_id=payload.get('tenant_id', self.tenant_id),
                roles=payload.get('roles', []),
                groups=payload.get('groups', []),
                app_roles=payload.get('app_roles', {}),
                token_type='jwt'
            )
            
            # Create new access token
            return self.create_jwt_token(user_context)
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None
    
    async def logout(self, token: str) -> bool:
        """Logout a user (invalidate token)."""
        try:
            # For JWT tokens, we would typically add to a blacklist
            # For Azure AD tokens, we would call the logout endpoint
            
            # Validate token first
            user_context = await self.validate_token(token)
            
            if user_context.token_type == 'azure_ad':
                # For Azure AD tokens, we could call the logout endpoint
                # But typically, the client handles this
                pass
            
            # Log the logout event
            logger.info(f"User {user_context.user_id} logged out")
            
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
    
    def get_login_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """Get the Azure AD login URL."""
        auth_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&scope=openid profile email User.Read"
            f"&response_mode=query"
        )
        
        if state:
            auth_url += f"&state={state}"
        
        return auth_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'scope': 'openid profile email User.Read',
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Code exchange failed: {str(e)}")
            return None
