import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AgentCapability {
  name: string;
  description: string;
  parameters: string[];
}

interface Agent {
  id: string;
  name: string;
  type: 'copilot_studio_1' | 'copilot_studio_2' | 'ai_foundry_1' | 'ai_foundry_2' | 'orchestrator';
  description: string;
  capabilities: AgentCapability[];
  status: 'active' | 'inactive' | 'mock';
  version: string;
  lastUsed?: string;
  usage_count?: number;
  success_rate?: number;
}

interface AgentResponse {
  agentId: string;
  agentType: string;
  response: any;
  confidence: number;
  processingTime: number;
  timestamp: string;
  success: boolean;
  error?: string;
}

interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  agentResponses: AgentResponse[];
  isLoading: boolean;
  error: string | null;
  lastRefresh: string | null;
  metrics: {
    totalQueries: number;
    averageResponseTime: number;
    successRate: number;
    topPerformingAgent: string | null;
  };
}

const initialState: AgentState = {
  agents: [],
  selectedAgent: null,
  agentResponses: [],
  isLoading: false,
  error: null,
  lastRefresh: null,
  metrics: {
    totalQueries: 0,
    averageResponseTime: 0,
    successRate: 0,
    topPerformingAgent: null,
  },
};

const agentSlice = createSlice({
  name: 'agent',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setAgents: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload;
      state.lastRefresh = new Date().toISOString();
    },
    addAgent: (state, action: PayloadAction<Agent>) => {
      state.agents.push(action.payload);
    },
    updateAgent: (state, action: PayloadAction<Partial<Agent> & { id: string }>) => {
      const index = state.agents.findIndex(agent => agent.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = { ...state.agents[index], ...action.payload };
      }
    },
    removeAgent: (state, action: PayloadAction<string>) => {
      state.agents = state.agents.filter(agent => agent.id !== action.payload);
    },
    setSelectedAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    addAgentResponse: (state, action: PayloadAction<AgentResponse>) => {
      state.agentResponses.unshift(action.payload);
      // Keep only the last 100 responses
      if (state.agentResponses.length > 100) {
        state.agentResponses = state.agentResponses.slice(0, 100);
      }
    },
    clearAgentResponses: (state) => {
      state.agentResponses = [];
    },
    updateMetrics: (state, action: PayloadAction<Partial<AgentState['metrics']>>) => {
      state.metrics = { ...state.metrics, ...action.payload };
    },
    incrementUsageCount: (state, action: PayloadAction<string>) => {
      const agent = state.agents.find(a => a.id === action.payload);
      if (agent) {
        agent.usage_count = (agent.usage_count || 0) + 1;
        agent.lastUsed = new Date().toISOString();
      }
    },
    updateAgentSuccessRate: (state, action: PayloadAction<{ agentId: string; success: boolean }>) => {
      const agent = state.agents.find(a => a.id === action.payload.agentId);
      if (agent) {
        const currentCount = agent.usage_count || 0;
        const currentRate = agent.success_rate || 0;
        const newRate = action.payload.success
          ? (currentRate * currentCount + 1) / (currentCount + 1)
          : (currentRate * currentCount) / (currentCount + 1);
        agent.success_rate = newRate;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setError,
  setAgents,
  addAgent,
  updateAgent,
  removeAgent,
  setSelectedAgent,
  addAgentResponse,
  clearAgentResponses,
  updateMetrics,
  incrementUsageCount,
  updateAgentSuccessRate,
  clearError,
} = agentSlice.actions;

export default agentSlice.reducer;

// Selectors
export const selectAgents = (state: { agent: AgentState }) => state.agent.agents;
export const selectSelectedAgent = (state: { agent: AgentState }) => state.agent.selectedAgent;
export const selectAgentResponses = (state: { agent: AgentState }) => state.agent.agentResponses;
export const selectAgentLoading = (state: { agent: AgentState }) => state.agent.isLoading;
export const selectAgentError = (state: { agent: AgentState }) => state.agent.error;
export const selectAgentMetrics = (state: { agent: AgentState }) => state.agent.metrics;
export const selectAgentByType = (type: Agent['type']) => (state: { agent: AgentState }) => 
  state.agent.agents.filter(agent => agent.type === type);
export const selectActiveAgents = (state: { agent: AgentState }) => 
  state.agent.agents.filter(agent => agent.status === 'active');
export const selectAgentById = (id: string) => (state: { agent: AgentState }) => 
  state.agent.agents.find(agent => agent.id === id);
