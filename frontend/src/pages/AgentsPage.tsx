import React from 'react';

const AgentsPage: React.FC = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Agents</h1>
      <p>Manage your multiagent system</p>
      
      <div style={{ marginTop: '2rem' }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '1.5rem', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '1rem'
        }}>
          <h3>Copilot Studio Agent</h3>
          <p>Status: Online</p>
          <p>Handles user conversations and intent routing</p>
        </div>
        
        <div style={{ 
          backgroundColor: 'white', 
          padding: '1.5rem', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '1rem'
        }}>
          <h3>Azure AI Foundry Agent</h3>
          <p>Status: Online</p>
          <p>Processes complex queries and AI tasks</p>
        </div>
        
        <div style={{ 
          backgroundColor: 'white', 
          padding: '1.5rem', 
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '1rem'
        }}>
          <h3>Orchestrator</h3>
          <p>Status: Online</p>
          <p>Coordinates between agents and manages workflows</p>
        </div>
      </div>
    </div>
  );
};

export default AgentsPage;
