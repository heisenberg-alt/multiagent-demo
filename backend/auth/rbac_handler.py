"""
Role-Based Access Control (RBAC) handler for the multiagent system.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import json

from utils.config import Config
from models.agent_models import UserContext, AgentType

logger = logging.getLogger(__name__)

class Permission(Enum):
    """System permissions."""
    COPILOT_STUDIO_ACCESS = "copilot_studio_access"
    AI_FOUNDRY_ACCESS = "ai_foundry_access"
    PRO_CODE_ACCESS = "pro_code_access"
    ADMIN_ACCESS = "admin_access"
    ORCHESTRATION_ACCESS = "orchestration_access"
    CHAT_ACCESS = "chat_access"
    METRICS_READ = "metrics_read"
    USER_MANAGEMENT = "user_management"

class Role(Enum):
    """System roles."""
    ADMIN = "admin"
    POWER_USER = "power_user"
    STANDARD_USER = "standard_user"
    GUEST = "guest"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.COPILOT_STUDIO_ACCESS,
        Permission.AI_FOUNDRY_ACCESS,
        Permission.PRO_CODE_ACCESS,
        Permission.ADMIN_ACCESS,
        Permission.ORCHESTRATION_ACCESS,
        Permission.CHAT_ACCESS,
        Permission.METRICS_READ,
        Permission.USER_MANAGEMENT
    ],
    Role.POWER_USER: [
        Permission.COPILOT_STUDIO_ACCESS,
        Permission.AI_FOUNDRY_ACCESS,
        Permission.PRO_CODE_ACCESS,
        Permission.ORCHESTRATION_ACCESS,
        Permission.CHAT_ACCESS
    ],
    Role.STANDARD_USER: [
        Permission.COPILOT_STUDIO_ACCESS,
        Permission.CHAT_ACCESS
    ],
    Role.GUEST: [
        Permission.CHAT_ACCESS
    ]
}

# Agent type to permission mapping
AGENT_PERMISSIONS = {
    AgentType.COPILOT_STUDIO_1: Permission.COPILOT_STUDIO_ACCESS,
    AgentType.COPILOT_STUDIO_2: Permission.COPILOT_STUDIO_ACCESS,
    AgentType.AI_FOUNDRY_1: Permission.AI_FOUNDRY_ACCESS,
    AgentType.AI_FOUNDRY_2: Permission.AI_FOUNDRY_ACCESS,
    AgentType.ORCHESTRATOR: Permission.ORCHESTRATION_ACCESS
}

class RBACHandler:
    """Handles role-based access control for the multiagent system."""
    
    def __init__(self, config: Config):
        """Initialize RBAC handler."""
        self.config = config
        self.rbac_enabled = config.rbac_enabled
        self.default_permissions = config.default_user_permissions
        
        # In-memory storage for user permissions (in production, use a database)
        self.user_permissions: Dict[str, Dict[str, Any]] = {}
        self.user_roles: Dict[str, List[Role]] = {}
        
        # Azure AD group to role mapping
        self.group_role_mapping: Dict[str, Role] = {}
        
        logger.info(f"RBAC handler initialized (enabled: {self.rbac_enabled})")
    
    def has_permission(self, user_context: UserContext, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        if not self.rbac_enabled:
            return True
        
        try:
            # Check if user is explicitly granted permission
            user_permissions = self.get_user_permissions(user_context.user_id)
            if permission.value in user_permissions.get('explicit_permissions', []):
                return True
            
            # Check role-based permissions
            user_roles = self.get_user_roles(user_context)
            for role in user_roles:
                if permission in ROLE_PERMISSIONS.get(role, []):
                    return True
            
            # Check Azure AD group-based permissions
            if user_context.groups:
                for group_id in user_context.groups:
                    group_role = self.group_role_mapping.get(group_id)
                    if group_role and permission in ROLE_PERMISSIONS.get(group_role, []):
                        return True
            
            # Check Azure AD app roles
            if user_context.app_roles:
                for app_role in user_context.app_roles:
                    role = self._map_app_role_to_system_role(app_role)
                    if role and permission in ROLE_PERMISSIONS.get(role, []):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed for user {user_context.user_id}: {str(e)}")
            return False
    
    def has_agent_permission(self, user_context: UserContext, agent_type: AgentType) -> bool:
        """Check if user has permission to access a specific agent type."""
        required_permission = AGENT_PERMISSIONS.get(agent_type)
        if not required_permission:
            logger.warning(f"No permission mapping found for agent type: {agent_type}")
            return False
        
        return self.has_permission(user_context, required_permission)
    
    def is_admin(self, user_context: UserContext) -> bool:
        """Check if user has admin privileges."""
        return self.has_permission(user_context, Permission.ADMIN_ACCESS)
    
    def get_user_roles(self, user_context: UserContext) -> List[Role]:
        """Get user's roles."""
        roles = []
        
        # Check explicitly assigned roles
        user_roles = self.user_roles.get(user_context.user_id, [])
        roles.extend(user_roles)
        
        # Check Azure AD group-based roles
        if user_context.groups:
            for group_id in user_context.groups:
                group_role = self.group_role_mapping.get(group_id)
                if group_role and group_role not in roles:
                    roles.append(group_role)
        
        # Check Azure AD app roles
        if user_context.app_roles:
            for app_role in user_context.app_roles:
                role = self._map_app_role_to_system_role(app_role)
                if role and role not in roles:
                    roles.append(role)
        
        # Default role if no roles assigned
        if not roles:
            roles.append(Role.GUEST)
        
        return roles
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get user's permissions."""
        return self.user_permissions.get(user_id, {
            'explicit_permissions': [],
            'roles': [],
            'groups': [],
            'last_updated': None
        })
    
    def update_user_permissions(self, user_id: str, permissions: Dict[str, Any]) -> bool:
        """Update user's permissions."""
        try:
            from datetime import datetime
            
            # Validate permissions
            if 'explicit_permissions' in permissions:
                valid_permissions = [p.value for p in Permission]
                for perm in permissions['explicit_permissions']:
                    if perm not in valid_permissions:
                        raise ValueError(f"Invalid permission: {perm}")
            
            # Update permissions
            current_permissions = self.get_user_permissions(user_id)
            current_permissions.update(permissions)
            current_permissions['last_updated'] = datetime.utcnow().isoformat()
            
            self.user_permissions[user_id] = current_permissions
            
            logger.info(f"Updated permissions for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update permissions for user {user_id}: {str(e)}")
            return False
    
    def assign_role(self, user_id: str, role: Role) -> bool:
        """Assign a role to a user."""
        try:
            if user_id not in self.user_roles:
                self.user_roles[user_id] = []
            
            if role not in self.user_roles[user_id]:
                self.user_roles[user_id].append(role)
                logger.info(f"Assigned role {role.value} to user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role {role.value} to user {user_id}: {str(e)}")
            return False
    
    def remove_role(self, user_id: str, role: Role) -> bool:
        """Remove a role from a user."""
        try:
            if user_id in self.user_roles and role in self.user_roles[user_id]:
                self.user_roles[user_id].remove(role)
                logger.info(f"Removed role {role.value} from user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove role {role.value} from user {user_id}: {str(e)}")
            return False
    
    def map_group_to_role(self, group_id: str, role: Role):
        """Map an Azure AD group to a system role."""
        self.group_role_mapping[group_id] = role
        logger.info(f"Mapped group {group_id} to role {role.value}")
    
    def _map_app_role_to_system_role(self, app_role: str) -> Optional[Role]:
        """Map Azure AD app role to system role."""
        app_role_mapping = {
            'Admin': Role.ADMIN,
            'PowerUser': Role.POWER_USER,
            'User': Role.STANDARD_USER,
            'Guest': Role.GUEST
        }
        
        return app_role_mapping.get(app_role)
    
    def get_accessible_agents(self, user_context: UserContext) -> List[AgentType]:
        """Get list of agents the user can access."""
        accessible_agents = []
        
        for agent_type in AgentType:
            if self.has_agent_permission(user_context, agent_type):
                accessible_agents.append(agent_type)
        
        return accessible_agents
    
    def can_orchestrate(self, user_context: UserContext) -> bool:
        """Check if user can use orchestration features."""
        return self.has_permission(user_context, Permission.ORCHESTRATION_ACCESS)
    
    def can_manage_users(self, user_context: UserContext) -> bool:
        """Check if user can manage other users."""
        return self.has_permission(user_context, Permission.USER_MANAGEMENT)
    
    def can_view_metrics(self, user_context: UserContext) -> bool:
        """Check if user can view system metrics."""
        return self.has_permission(user_context, Permission.METRICS_READ)
    
    def validate_access(self, user_context: UserContext, resource: str, action: str) -> bool:
        """Validate user access to a specific resource and action."""
        # Define resource-action to permission mapping
        access_matrix = {
            ('agents', 'list'): Permission.CHAT_ACCESS,
            ('agents', 'query'): Permission.CHAT_ACCESS,
            ('orchestrate', 'query'): Permission.ORCHESTRATION_ACCESS,
            ('chat', 'create'): Permission.CHAT_ACCESS,
            ('chat', 'send'): Permission.CHAT_ACCESS,
            ('users', 'list'): Permission.USER_MANAGEMENT,
            ('users', 'update'): Permission.USER_MANAGEMENT,
            ('metrics', 'read'): Permission.METRICS_READ,
        }
        
        required_permission = access_matrix.get((resource, action))
        if not required_permission:
            logger.warning(f"No permission mapping found for {resource}:{action}")
            return False
        
        return self.has_permission(user_context, required_permission)
    
    def get_user_summary(self, user_context: UserContext) -> Dict[str, Any]:
        """Get a summary of user's permissions and access."""
        roles = self.get_user_roles(user_context)
        permissions = []
        
        for role in roles:
            permissions.extend([p.value for p in ROLE_PERMISSIONS.get(role, [])])
        
        # Remove duplicates
        permissions = list(set(permissions))
        
        accessible_agents = [agent.value for agent in self.get_accessible_agents(user_context)]
        
        return {
            'user_id': user_context.user_id,
            'roles': [role.value for role in roles],
            'permissions': permissions,
            'accessible_agents': accessible_agents,
            'can_orchestrate': self.can_orchestrate(user_context),
            'can_manage_users': self.can_manage_users(user_context),
            'can_view_metrics': self.can_view_metrics(user_context),
            'is_admin': self.is_admin(user_context)
        }
