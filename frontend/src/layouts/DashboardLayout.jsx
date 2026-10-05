import React, { useState, useEffect } from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';
import ToastContainer from '../components/ToastContainer';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (!user || user.preferences?.notifications?.systemNotifications === false) return;

    let lastNotificationId = null;

    const checkNotifications = async () => {
      try {
        const res = await api.get('/notifications');
        const unread = res.data.filter(n => !n.isRead);
        if (unread.length > 0) {
          const latest = unread[0];
          if (lastNotificationId !== latest.notificationId) {
            lastNotificationId = latest.notificationId;
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification(latest.title, { body: latest.message });
            }
          }
        }
      } catch (err) {
        console.error("Error fetching notifications:", err);
      }
    };

    checkNotifications();
    const intervalId = setInterval(checkNotifications, 10000);
    return () => clearInterval(intervalId);
  }, [user]);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg-light)] text-slate-800">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden w-full relative">
        <Topbar setSidebarOpen={setSidebarOpen} />
        
        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 relative">
          <div key={location.pathname} className="max-w-7xl mx-auto w-full page-transition">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Toast Notification Host */}
      <ToastContainer />
    </div>
  );
};

export default DashboardLayout;
