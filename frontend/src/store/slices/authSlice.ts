import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { AccountInfo } from '@azure/msal-browser';

interface UserProfile {
  id: string;
  displayName: string;
  email: string;
  jobTitle?: string;
  department?: string;
  roles: string[];
  permissions: string[];
}

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  account: AccountInfo | null;
  userProfile: UserProfile | null;
  accessToken: string | null;
  error: string | null;
  loginType: 'redirect' | 'popup' | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  isLoading: false,
  account: null,
  userProfile: null,
  accessToken: null,
  error: null,
  loginType: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state, action: PayloadAction<'redirect' | 'popup'>) => {
      state.isLoading = true;
      state.error = null;
      state.loginType = action.payload;
    },
    loginSuccess: (state, action: PayloadAction<{
      account: AccountInfo;
      accessToken: string;
    }>) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.account = action.payload.account;
      state.accessToken = action.payload.accessToken;
      state.error = null;
    },
    loginFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.account = null;
      state.accessToken = null;
      state.error = action.payload;
      state.loginType = null;
    },
    logoutStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    logoutSuccess: (state) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.account = null;
      state.userProfile = null;
      state.accessToken = null;
      state.error = null;
      state.loginType = null;
    },
    setUserProfile: (state, action: PayloadAction<UserProfile>) => {
      state.userProfile = action.payload;
    },
    updateUserRoles: (state, action: PayloadAction<string[]>) => {
      if (state.userProfile) {
        state.userProfile.roles = action.payload;
      }
    },
    updateUserPermissions: (state, action: PayloadAction<string[]>) => {
      if (state.userProfile) {
        state.userProfile.permissions = action.payload;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const {
  loginStart,
  loginSuccess,
  loginFailure,
  logoutStart,
  logoutSuccess,
  setUserProfile,
  updateUserRoles,
  updateUserPermissions,
  clearError,
  setLoading,
} = authSlice.actions;

export default authSlice.reducer;

// Selectors
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectUserProfile = (state: { auth: AuthState }) => state.auth.userProfile;
export const selectUserRoles = (state: { auth: AuthState }) => state.auth.userProfile?.roles || [];
export const selectUserPermissions = (state: { auth: AuthState }) => state.auth.userProfile?.permissions || [];
export const selectIsLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectError = (state: { auth: AuthState }) => state.auth.error;
