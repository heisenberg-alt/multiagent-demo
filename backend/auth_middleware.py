"""
Azure AD JWT Token Validation Middleware for FastAPI
"""
import os
import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import json
from functools import lru_cache

security = HTTPBearer()

# Configuration
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID', '22160f2d-f7a0-4f0f-b25e-ce5b8f2b98ab')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID', 'b141e5c0-fccb-4859-9de5-a84c1304ee9d')
AZURE_AUDIENCE = os.getenv('AZURE_AUDIENCE', 'api://multiagent-demo-api-487900148')

@lru_cache()
def get_azure_public_keys():
    """Fetch Azure AD public keys for JWT validation"""
    try:
        keys_url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"
        with httpx.Client() as client:
            response = client.get(keys_url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Azure AD public keys: {str(e)}"
        )

def get_rsa_key(token: str) -> Optional[Dict[str, Any]]:
    """Get the RSA key for token validation"""
    try:
        # Decode token header to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')
        
        if not kid:
            return None
            
        # Get public keys from Azure AD
        jwks = get_azure_public_keys()
        
        # Find matching key
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                return {
                    'kty': key.get('kty'),
                    'use': key.get('use'),
                    'n': key.get('n'),
                    'e': key.get('e')
                }
        return None
    except Exception:
        return None

def validate_jwt_token(token: str) -> Dict[str, Any]:
    """Validate Azure AD JWT token"""
    try:
        # Get RSA key
        rsa_key = get_rsa_key(token)
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key"
            )
        
        # Construct the key for PyJWT
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
        from cryptography.hazmat.primitives import serialization
        import base64
        
        def base64url_decode(input_str):
            """Decode base64url string"""
            input_str += '=' * (4 - len(input_str) % 4)
            return base64.urlsafe_b64decode(input_str)
        
        n = int.from_bytes(base64url_decode(rsa_key['n']), 'big')
        e = int.from_bytes(base64url_decode(rsa_key['e']), 'big')
        
        public_numbers = RSAPublicNumbers(e, n)
        public_key = public_numbers.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Validate token
        payload = jwt.decode(
            token,
            pem,
            algorithms=['RS256'],
            audience=AZURE_AUDIENCE,
            issuer=f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0'
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = validate_jwt_token(token)
    
    return {
        'user_id': payload.get('oid'),
        'email': payload.get('email') or payload.get('preferred_username'),
        'name': payload.get('name'),
        'tenant_id': payload.get('tid'),
        'app_id': payload.get('appid'),
        'roles': payload.get('roles', []),
        'scopes': payload.get('scp', '').split(' ') if payload.get('scp') else []
    }

def require_scope(required_scope: str):
    """Decorator to require specific scope"""
    def decorator(user: Dict[str, Any] = Depends(get_current_user)):
        if required_scope not in user.get('scopes', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scope '{required_scope}' not found"
            )
        return user
    return decorator

def require_role(required_role: str):
    """Decorator to require specific role"""
    def decorator(user: Dict[str, Any] = Depends(get_current_user)):
        if required_role not in user.get('roles', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role '{required_role}' not found"
            )
        return user
    return decorator
