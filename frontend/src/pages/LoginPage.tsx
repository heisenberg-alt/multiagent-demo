import React from 'react';

const LoginPage: React.FC = () => {
  const handleLogin = async () => {
    // Simple login logic
    console.log('Login clicked');
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        textAlign: 'center',
        maxWidth: '400px',
        width: '100%'
      }}>
        <h1>Multiagent Demo</h1>
        <h2>Orchestrated AI Agents</h2>
        <p>Sign in to access the multiagent system with Copilot Studio and Azure AI Foundry agents.</p>
        <button
          onClick={handleLogin}
          style={{
            backgroundColor: '#0078d4',
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
            marginTop: '1rem'
          }}
        >
          Sign In with Microsoft
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
