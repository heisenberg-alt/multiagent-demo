import { Configuration, RedirectRequest, PopupRequest } from '@azure/msal-browser';

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.REACT_APP_AZURE_CLIENT_ID || '480ca618-5f28-494b-bf9d-d1a803b8a840',
    authority: process.env.REACT_APP_AZURE_AUTHORITY || 'https://login.microsoftonline.com/22160f2d-f7a0-4f0f-b25e-ce5b8f2b98ab',
    redirectUri: process.env.REACT_APP_REDIRECT_URI || 'https://green-sand-0a95fec0f.1.azurestaticapps.net',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

// Add scopes for login request
export const loginRequest: RedirectRequest = {
  scopes: [
    'openid',
    'profile',
    'email',
    'api://multiagent-demo-api-487900148/access_as_user'
  ],
};

// Add scopes for popup login request
export const popupRequest: PopupRequest = {
  scopes: [
    'openid',
    'profile', 
    'email',
    'api://multiagent-demo-api-487900148/access_as_user'
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
