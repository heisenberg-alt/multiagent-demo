import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  autoHide?: boolean;
  duration?: number;
}

interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  notifications: Notification[];
  loading: {
    global: boolean;
    components: { [key: string]: boolean };
  };
  modals: {
    agentDetails: boolean;
    settings: boolean;
    about: boolean;
  };
  preferences: {
    autoSave: boolean;
    notifications: boolean;
    animationsEnabled: boolean;
    compactMode: boolean;
  };
  layout: {
    chatPanelWidth: number;
    agentPanelWidth: number;
    showMetrics: boolean;
    showHelp: boolean;
  };
}

const initialState: UIState = {
  theme: 'light',
  sidebarOpen: true,
  notifications: [],
  loading: {
    global: false,
    components: {},
  },
  modals: {
    agentDetails: false,
    settings: false,
    about: false,
  },
  preferences: {
    autoSave: true,
    notifications: true,
    animationsEnabled: true,
    compactMode: false,
  },
  layout: {
    chatPanelWidth: 400,
    agentPanelWidth: 300,
    showMetrics: true,
    showHelp: false,
  },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
    setComponentLoading: (state, action: PayloadAction<{ component: string; loading: boolean }>) => {
      state.loading.components[action.payload.component] = action.payload.loading;
    },
    clearComponentLoading: (state, action: PayloadAction<string>) => {
      delete state.loading.components[action.payload];
    },
    openModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = true;
    },
    closeModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = false;
    },
    closeAllModals: (state) => {
      Object.keys(state.modals).forEach((key) => {
        state.modals[key as keyof UIState['modals']] = false;
      });
    },
    updatePreferences: (state, action: PayloadAction<Partial<UIState['preferences']>>) => {
      state.preferences = { ...state.preferences, ...action.payload };
    },
    updateLayout: (state, action: PayloadAction<Partial<UIState['layout']>>) => {
      state.layout = { ...state.layout, ...action.payload };
    },
    setChatPanelWidth: (state, action: PayloadAction<number>) => {
      state.layout.chatPanelWidth = action.payload;
    },
    setAgentPanelWidth: (state, action: PayloadAction<number>) => {
      state.layout.agentPanelWidth = action.payload;
    },
    toggleMetrics: (state) => {
      state.layout.showMetrics = !state.layout.showMetrics;
    },
    toggleHelp: (state) => {
      state.layout.showHelp = !state.layout.showHelp;
    },
    resetLayout: (state) => {
      state.layout = initialState.layout;
    },
  },
});

export const {
  setTheme,
  toggleSidebar,
  setSidebarOpen,
  addNotification,
  removeNotification,
  clearNotifications,
  setGlobalLoading,
  setComponentLoading,
  clearComponentLoading,
  openModal,
  closeModal,
  closeAllModals,
  updatePreferences,
  updateLayout,
  setChatPanelWidth,
  setAgentPanelWidth,
  toggleMetrics,
  toggleHelp,
  resetLayout,
} = uiSlice.actions;

export default uiSlice.reducer;

// Selectors
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectSidebarOpen = (state: { ui: UIState }) => state.ui.sidebarOpen;
export const selectNotifications = (state: { ui: UIState }) => state.ui.notifications;
export const selectGlobalLoading = (state: { ui: UIState }) => state.ui.loading.global;
export const selectComponentLoading = (component: string) => (state: { ui: UIState }) => 
  state.ui.loading.components[component] || false;
export const selectModals = (state: { ui: UIState }) => state.ui.modals;
export const selectModalOpen = (modal: keyof UIState['modals']) => (state: { ui: UIState }) => 
  state.ui.modals[modal];
export const selectPreferences = (state: { ui: UIState }) => state.ui.preferences;
export const selectLayout = (state: { ui: UIState }) => state.ui.layout;
export const selectUnreadNotifications = (state: { ui: UIState }) => 
  state.ui.notifications.filter(n => n.type === 'error' || n.type === 'warning').length;
