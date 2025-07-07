import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  agentId?: string;
  agentType?: string;
  metadata?: {
    confidence?: number;
    processingTime?: number;
    tokens?: number;
  };
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
  agentId?: string;
  agentType?: string;
  isActive: boolean;
}

interface ChatState {
  sessions: ChatSession[];
  activeSession: ChatSession | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  streamingMessage: string | null;
  statistics: {
    totalMessages: number;
    totalSessions: number;
    averageSessionLength: number;
    mostUsedAgent: string | null;
  };
}

const initialState: ChatState = {
  sessions: [],
  activeSession: null,
  isLoading: false,
  isTyping: false,
  error: null,
  streamingMessage: null,
  statistics: {
    totalMessages: 0,
    totalSessions: 0,
    averageSessionLength: 0,
    mostUsedAgent: null,
  },
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setSessions: (state, action: PayloadAction<ChatSession[]>) => {
      state.sessions = action.payload;
    },
    addSession: (state, action: PayloadAction<ChatSession>) => {
      state.sessions.unshift(action.payload);
    },
    updateSession: (state, action: PayloadAction<Partial<ChatSession> & { id: string }>) => {
      const index = state.sessions.findIndex(session => session.id === action.payload.id);
      if (index !== -1) {
        state.sessions[index] = { ...state.sessions[index], ...action.payload };
      }
    },
    removeSession: (state, action: PayloadAction<string>) => {
      state.sessions = state.sessions.filter(session => session.id !== action.payload);
      if (state.activeSession?.id === action.payload) {
        state.activeSession = null;
      }
    },
    setActiveSession: (state, action: PayloadAction<ChatSession | null>) => {
      state.activeSession = action.payload;
      // Mark all sessions as inactive, then mark the selected one as active
      state.sessions.forEach(session => {
        session.isActive = false;
      });
      if (action.payload) {
        const index = state.sessions.findIndex(s => s.id === action.payload!.id);
        if (index !== -1) {
          state.sessions[index].isActive = true;
        }
      }
    },
    addMessage: (state, action: PayloadAction<{
      sessionId: string;
      message: ChatMessage;
    }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId);
      if (session) {
        session.messages.push(action.payload.message);
        session.updatedAt = new Date().toISOString();
      }
      // Also update active session if it's the same
      if (state.activeSession?.id === action.payload.sessionId) {
        state.activeSession.messages.push(action.payload.message);
        state.activeSession.updatedAt = new Date().toISOString();
      }
    },
    updateMessage: (state, action: PayloadAction<{
      sessionId: string;
      messageId: string;
      updates: Partial<ChatMessage>;
    }>) => {
      const session = state.sessions.find(s => s.id === action.payload.sessionId);
      if (session) {
        const messageIndex = session.messages.findIndex(m => m.id === action.payload.messageId);
        if (messageIndex !== -1) {
          session.messages[messageIndex] = { ...session.messages[messageIndex], ...action.payload.updates };
        }
      }
      // Also update active session if it's the same
      if (state.activeSession?.id === action.payload.sessionId) {
        const messageIndex = state.activeSession.messages.findIndex(m => m.id === action.payload.messageId);
        if (messageIndex !== -1) {
          state.activeSession.messages[messageIndex] = { ...state.activeSession.messages[messageIndex], ...action.payload.updates };
        }
      }
    },
    clearMessages: (state, action: PayloadAction<string>) => {
      const session = state.sessions.find(s => s.id === action.payload);
      if (session) {
        session.messages = [];
        session.updatedAt = new Date().toISOString();
      }
      // Also update active session if it's the same
      if (state.activeSession?.id === action.payload) {
        state.activeSession.messages = [];
        state.activeSession.updatedAt = new Date().toISOString();
      }
    },
    setStreamingMessage: (state, action: PayloadAction<string | null>) => {
      state.streamingMessage = action.payload;
    },
    updateStatistics: (state, action: PayloadAction<Partial<ChatState['statistics']>>) => {
      state.statistics = { ...state.statistics, ...action.payload };
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setTyping,
  setError,
  setSessions,
  addSession,
  updateSession,
  removeSession,
  setActiveSession,
  addMessage,
  updateMessage,
  clearMessages,
  setStreamingMessage,
  updateStatistics,
  clearError,
} = chatSlice.actions;

export default chatSlice.reducer;

// Selectors
export const selectChatSessions = (state: { chat: ChatState }) => state.chat.sessions;
export const selectActiveSession = (state: { chat: ChatState }) => state.chat.activeSession;
export const selectChatLoading = (state: { chat: ChatState }) => state.chat.isLoading;
export const selectChatTyping = (state: { chat: ChatState }) => state.chat.isTyping;
export const selectChatError = (state: { chat: ChatState }) => state.chat.error;
export const selectStreamingMessage = (state: { chat: ChatState }) => state.chat.streamingMessage;
export const selectChatStatistics = (state: { chat: ChatState }) => state.chat.statistics;
export const selectSessionById = (id: string) => (state: { chat: ChatState }) => 
  state.chat.sessions.find(session => session.id === id);
export const selectRecentSessions = (limit: number = 10) => (state: { chat: ChatState }) => 
  state.chat.sessions.slice(0, limit);
export const selectSessionsByAgent = (agentId: string) => (state: { chat: ChatState }) => 
  state.chat.sessions.filter(session => session.agentId === agentId);
