import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useMsal, useIsAuthenticated } from '@azure/msal-react';
import { Box, Snackbar, Alert } from '@mui/material';
import { AnimatePresence } from 'framer-motion';

// Components
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AgentsPage from './pages/AgentsPage';
import ChatPage from './pages/ChatPage';
import SettingsPage from './pages/SettingsPage';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoadingSpinner from './components/LoadingSpinner';
import NotificationCenter from './components/NotificationCenter';

// Store
import { AppDispatch } from './store/store';
import { selectIsLoading, selectError } from './store/slices/authSlice';
import { selectNotifications, removeNotification } from './store/slices/uiSlice';

// Services
import { authService } from './services/authService';
import { agentService } from './services/agentService';

// Styles
import './styles/App.css';

const App: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useSelector(selectIsLoading);
  const error = useSelector(selectError);
  const notifications = useSelector(selectNotifications);

  useEffect(() => {
    // Initialize authentication
    const initializeAuth = async () => {
      try {
        await authService.initialize(instance);
        
        // If authenticated, load user data and agents
        if (isAuthenticated) {
          await Promise.all([
            authService.getUserProfile(),
            agentService.loadAgents(),
          ]);
        }
      } catch (error) {
        console.error('Failed to initialize app:', error);
      }
    };

    initializeAuth();
  }, [instance, isAuthenticated]);

  const handleNotificationClose = (notificationId: string) => {
    dispatch(removeNotification(notificationId));
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
      >
        <LoadingSpinner size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AnimatePresence mode="wait">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginPage />
              )
            }
          />
          <Route
            path="/"
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/agents"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout>
                  <AgentsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout>
                  <ChatPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:sessionId"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout>
                  <ChatPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute isAuthenticated={isAuthenticated}>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="*"
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
            }
          />
        </Routes>
      </AnimatePresence>

      {/* Notification Center */}
      <NotificationCenter
        notifications={notifications}
        onClose={handleNotificationClose}
      />

      {/* Global Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => dispatch({ type: 'auth/clearError' })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => dispatch({ type: 'auth/clearError' })}
          severity="error"
          sx={{ width: '100%' }}
        >
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default App;
