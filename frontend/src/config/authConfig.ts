import { Configuration, RedirectRequest, PopupRequest } from '@azure/msal-browser';

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_AZURE_CLIENT_ID || 'your-client-id',
    authority: `https://login.microsoftonline.com/${process.env.REACT_APP_AZURE_TENANT_ID || 'common'}`,
    redirectUri: process.env.REACT_APP_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation: 'localStorage',
    storeAuthStateInCookie: false,
  },
};

// Add scopes for login request
export const loginRequest: RedirectRequest = {
  scopes: [
    'openid',
    'profile',
    'email',
    'User.Read',
    'Mail.Read',
    'Files.ReadWrite',
    'Sites.ReadWrite.All',
    'Team.ReadBasic.All',
    'Channel.ReadBasic.All'
  ],
};

// Add scopes for popup login request
export const popupRequest: PopupRequest = {
  scopes: [
    'openid',
    'profile',
    'email',
    'User.Read',
    'Mail.Read',
    'Files.ReadWrite',
    'Sites.ReadWrite.All',
    'Team.ReadBasic.All',
    'Channel.ReadBasic.All'
  ],
};

// Graph API configuration
export const graphConfig = {
  graphMeEndpoint: 'https://graph.microsoft.com/v1.0/me',
  graphMailEndpoint: 'https://graph.microsoft.com/v1.0/me/messages',
  graphFilesEndpoint: 'https://graph.microsoft.com/v1.0/me/drive/root/children',
};

// Backend API configuration
export const apiConfig = {
  backendUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
  endpoints: {
    health: '/health',
    agents: '/agents',
    chat: '/chat',
    orchestrate: '/orchestrate',
    permissions: '/permissions',
    metrics: '/metrics',
  },
};
