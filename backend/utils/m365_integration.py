"""
Microsoft 365 SDK integration for accessing M365 services and data.
This module provides integration with Microsoft Graph API and M365 services.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

from ..utils.config import Config
from ..utils.logger import get_logger
from ..utils.telemetry import telemetry_client

logger = get_logger(__name__)

class M365Integration:
    """Microsoft 365 SDK integration for Graph API and M365 services."""
    
    def __init__(self, config: Config):
        self.config = config
        self.credential = DefaultAzureCredential()
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        self.beta_endpoint = "https://graph.microsoft.com/beta"
        
        # Configuration
        self.tenant_id = config.get_setting("AZURE_TENANT_ID")
        self.client_id = config.get_setting("AZURE_CLIENT_ID")
        self.scopes = [
            "https://graph.microsoft.com/.default",
            "User.Read",
            "Mail.Read", 
            "Files.ReadWrite",
            "Sites.ReadWrite.All",
            "Team.ReadBasic.All",
            "Channel.ReadBasic.All"
        ]
        
        # Mock mode for development
        self.mock_mode = not all([self.tenant_id, self.client_id])
        
        if self.mock_mode:
            logger.warning("M365 integration running in mock mode - configuration missing")
        
        # Initialize session
        self.session = None
        self.access_token = None
        self.token_expires_at = None
    
    async def initialize(self) -> bool:
        """Initialize M365 integration."""
        try:
            if self.mock_mode:
                logger.info("M365 integration initialized in mock mode")
                return True
            
            # Get access token
            if not await self._get_access_token():
                logger.error("Failed to get access token for M365")
                return False
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'MultiagentDemo/1.0'
                }
            )
            
            # Test connection
            if await self._test_connection():
                logger.info("M365 integration initialized successfully")
                telemetry_client.track_event("m365_integration_initialized")
                return True
            else:
                logger.error("Failed to verify M365 connection")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize M365 integration: {e}")
            telemetry_client.track_exception(e)
            return False
    
    async def _get_access_token(self) -> bool:
        """Get access token for Microsoft Graph API."""
        try:
            token = self.credential.get_token("https://graph.microsoft.com/.default")
            self.access_token = token.token
            self.token_expires_at = datetime.fromtimestamp(token.expires_on)
            return True
            
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test connection to Microsoft Graph API."""
        try:
            if self.mock_mode:
                return True
            
            # Try to get current user profile
            url = f"{self.graph_endpoint}/me"
            async with self.session.get(url) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"M365 connection test failed: {e}")
            return False
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure access token is valid and refresh if needed."""
        try:
            if self.mock_mode:
                return True
            
            # Check if token is expired or will expire soon
            if self.token_expires_at and self.token_expires_at <= datetime.now() + timedelta(minutes=5):
                logger.info("Access token expired, refreshing...")
                if not await self._get_access_token():
                    return False
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    async def get_user_profile(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user profile from Microsoft Graph."""
        try:
            if self.mock_mode:
                return {
                    "id": "mock-user-id",
                    "displayName": "Mock User",
                    "mail": "mock.user@example.com",
                    "jobTitle": "Software Developer",
                    "department": "Engineering",
                    "officeLocation": "Remote",
                    "mobilePhone": "+1234567890",
                    "businessPhones": ["+1234567890"],
                    "userPrincipalName": "mock.user@example.com"
                }
            
            if not await self._ensure_valid_token():
                return {"error": "Authentication failed"}
            
            # Get user profile
            url = f"{self.graph_endpoint}/users/{user_id}" if user_id else f"{self.graph_endpoint}/me"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get user profile: {response.status}")
                    return {"error": f"Failed to get user profile: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return {"error": str(e)}
    
    async def get_user_emails(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user emails from Microsoft Graph."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": f"mock-email-{i}",
                        "subject": f"Mock Email {i}",
                        "bodyPreview": f"This is a mock email preview {i}",
                        "from": {"emailAddress": {"address": "sender@example.com", "name": "Sender Name"}},
                        "receivedDateTime": (datetime.now() - timedelta(days=i)).isoformat(),
                        "isRead": i % 2 == 0,
                        "importance": "normal"
                    }
                    for i in range(1, limit + 1)
                ]
            
            if not await self._ensure_valid_token():
                return []
            
            # Get user emails
            url = f"{self.graph_endpoint}/users/{user_id}/messages" if user_id else f"{self.graph_endpoint}/me/messages"
            url += f"?$top={limit}&$orderby=receivedDateTime desc"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    logger.error(f"Failed to get user emails: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get user emails: {e}")
            return []
    
    async def get_user_files(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user files from OneDrive."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": f"mock-file-{i}",
                        "name": f"document_{i}.docx",
                        "size": 1024 * i,
                        "createdDateTime": (datetime.now() - timedelta(days=i)).isoformat(),
                        "lastModifiedDateTime": (datetime.now() - timedelta(hours=i)).isoformat(),
                        "webUrl": f"https://example.sharepoint.com/mock-file-{i}",
                        "file": {"mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
                    }
                    for i in range(1, limit + 1)
                ]
            
            if not await self._ensure_valid_token():
                return []
            
            # Get user files
            url = f"{self.graph_endpoint}/users/{user_id}/drive/root/children" if user_id else f"{self.graph_endpoint}/me/drive/root/children"
            url += f"?$top={limit}&$orderby=lastModifiedDateTime desc"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    logger.error(f"Failed to get user files: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get user files: {e}")
            return []
    
    async def get_user_calendar_events(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user calendar events."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": f"mock-event-{i}",
                        "subject": f"Mock Meeting {i}",
                        "bodyPreview": f"This is a mock meeting {i}",
                        "start": {
                            "dateTime": (datetime.now() + timedelta(days=i)).isoformat(),
                            "timeZone": "UTC"
                        },
                        "end": {
                            "dateTime": (datetime.now() + timedelta(days=i, hours=1)).isoformat(),
                            "timeZone": "UTC"
                        },
                        "attendees": [
                            {"emailAddress": {"address": "attendee@example.com", "name": "Attendee Name"}}
                        ],
                        "organizer": {"emailAddress": {"address": "organizer@example.com", "name": "Organizer Name"}},
                        "location": {"displayName": "Conference Room 1"},
                        "importance": "normal"
                    }
                    for i in range(1, limit + 1)
                ]
            
            if not await self._ensure_valid_token():
                return []
            
            # Get calendar events
            url = f"{self.graph_endpoint}/users/{user_id}/events" if user_id else f"{self.graph_endpoint}/me/events"
            url += f"?$top={limit}&$orderby=start/dateTime"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    logger.error(f"Failed to get calendar events: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get calendar events: {e}")
            return []
    
    async def get_teams_info(self) -> List[Dict[str, Any]]:
        """Get user's Teams information."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": "mock-team-1",
                        "displayName": "Engineering Team",
                        "description": "Main engineering team",
                        "memberSettings": {"allowCreateUpdateChannels": True},
                        "channels": [
                            {"id": "mock-channel-1", "displayName": "General", "description": "General discussion"},
                            {"id": "mock-channel-2", "displayName": "Development", "description": "Development topics"}
                        ]
                    },
                    {
                        "id": "mock-team-2",
                        "displayName": "Project Alpha",
                        "description": "Project Alpha team",
                        "memberSettings": {"allowCreateUpdateChannels": False},
                        "channels": [
                            {"id": "mock-channel-3", "displayName": "General", "description": "General discussion"},
                            {"id": "mock-channel-4", "displayName": "Planning", "description": "Project planning"}
                        ]
                    }
                ]
            
            if not await self._ensure_valid_token():
                return []
            
            # Get user's teams
            url = f"{self.graph_endpoint}/me/joinedTeams"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    teams = data.get("value", [])
                    
                    # Get channels for each team
                    for team in teams:
                        team_id = team.get("id")
                        if team_id:
                            channels = await self._get_team_channels(team_id)
                            team["channels"] = channels
                    
                    return teams
                else:
                    logger.error(f"Failed to get Teams info: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get Teams info: {e}")
            return []
    
    async def _get_team_channels(self, team_id: str) -> List[Dict[str, Any]]:
        """Get channels for a specific team."""
        try:
            if self.mock_mode:
                return []
            
            url = f"{self.graph_endpoint}/teams/{team_id}/channels"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    logger.warning(f"Failed to get channels for team {team_id}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get team channels: {e}")
            return []
    
    async def search_content(self, query: str, entity_types: List[str] = None) -> Dict[str, Any]:
        """Search content across M365 services."""
        try:
            if self.mock_mode:
                return {
                    "searchResults": [
                        {
                            "hitId": f"mock-result-{i}",
                            "rank": i,
                            "summary": f"Mock search result {i} for query: {query}",
                            "resource": {
                                "displayName": f"Mock Document {i}",
                                "webUrl": f"https://example.sharepoint.com/mock-doc-{i}",
                                "lastModifiedDateTime": (datetime.now() - timedelta(days=i)).isoformat()
                            }
                        }
                        for i in range(1, 6)
                    ],
                    "totalResultsCount": 5
                }
            
            if not await self._ensure_valid_token():
                return {"error": "Authentication failed"}
            
            # Default entity types
            if entity_types is None:
                entity_types = ["driveItem", "message", "event", "site", "list", "listItem"]
            
            # Search request
            search_request = {
                "requests": [
                    {
                        "entityTypes": entity_types,
                        "query": {
                            "queryString": query
                        },
                        "from": 0,
                        "size": 20
                    }
                ]
            }
            
            url = f"{self.graph_endpoint}/search/query"
            
            async with self.session.post(url, json=search_request) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [{}])[0] if data.get("value") else {}
                else:
                    logger.error(f"Failed to search content: {response.status}")
                    return {"error": f"Search failed: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return {"error": str(e)}
    
    async def get_sharepoint_sites(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get SharePoint sites."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": f"mock-site-{i}",
                        "displayName": f"Mock Site {i}",
                        "webUrl": f"https://example.sharepoint.com/sites/mock-site-{i}",
                        "description": f"Mock SharePoint site {i}",
                        "createdDateTime": (datetime.now() - timedelta(days=i*30)).isoformat(),
                        "lastModifiedDateTime": (datetime.now() - timedelta(days=i)).isoformat()
                    }
                    for i in range(1, limit + 1)
                ]
            
            if not await self._ensure_valid_token():
                return []
            
            # Get SharePoint sites
            url = f"{self.graph_endpoint}/sites?$top={limit}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("value", [])
                else:
                    logger.error(f"Failed to get SharePoint sites: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get SharePoint sites: {e}")
            return []
    
    async def get_user_presence(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user presence information."""
        try:
            if self.mock_mode:
                return {
                    "id": "mock-user-id",
                    "availability": "Available",
                    "activity": "Available",
                    "statusMessage": {
                        "message": {
                            "content": "Working on multiagent demo",
                            "contentType": "text"
                        }
                    }
                }
            
            if not await self._ensure_valid_token():
                return {"error": "Authentication failed"}
            
            # Get user presence
            url = f"{self.graph_endpoint}/users/{user_id}/presence" if user_id else f"{self.graph_endpoint}/me/presence"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get user presence: {response.status}")
                    return {"error": f"Failed to get presence: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to get user presence: {e}")
            return {"error": str(e)}
    
    async def send_teams_message(self, team_id: str, channel_id: str, message: str) -> Dict[str, Any]:
        """Send a message to a Teams channel."""
        try:
            if self.mock_mode:
                return {
                    "id": "mock-message-id",
                    "subject": "Multiagent Demo Message",
                    "body": {"content": message},
                    "from": {"user": {"displayName": "Multiagent Demo"}},
                    "createdDateTime": datetime.now().isoformat(),
                    "messageType": "message"
                }
            
            if not await self._ensure_valid_token():
                return {"error": "Authentication failed"}
            
            # Send message
            url = f"{self.graph_endpoint}/teams/{team_id}/channels/{channel_id}/messages"
            
            message_data = {
                "body": {
                    "content": message,
                    "contentType": "text"
                }
            }
            
            async with self.session.post(url, json=message_data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    logger.error(f"Failed to send Teams message: {response.status}")
                    return {"error": f"Failed to send message: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Failed to send Teams message: {e}")
            return {"error": str(e)}
    
    async def get_integration_info(self) -> Dict[str, Any]:
        """Get M365 integration information."""
        return {
            "name": "Microsoft 365 Integration",
            "version": "1.0.0",
            "status": "active" if not self.mock_mode else "mock",
            "endpoints": {
                "graph": self.graph_endpoint,
                "beta": self.beta_endpoint
            },
            "supported_services": [
                "User Profile",
                "Outlook Mail",
                "OneDrive Files",
                "Calendar Events",
                "Microsoft Teams",
                "SharePoint Sites",
                "Content Search",
                "User Presence"
            ],
            "scopes": self.scopes,
            "mock_mode": self.mock_mode
        }
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("M365 integration cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during M365 integration cleanup: {e}")
