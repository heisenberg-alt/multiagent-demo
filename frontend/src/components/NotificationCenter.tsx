import React from 'react';

interface Notification {
  id: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
}

interface NotificationCenterProps {
  notifications: Notification[];
  onClose: (notificationId: string) => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ notifications, onClose }) => {
  return null; // Placeholder for notification center
};

export default NotificationCenter;
