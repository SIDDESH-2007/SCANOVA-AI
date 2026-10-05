import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from '../layouts/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import ProtectedRoute from './ProtectedRoute';
import ErrorBoundary from '../components/ErrorBoundary';

// Pages
import Login from '../pages/Login';
import Register from '../pages/Register';
import Dashboard from '../pages/Dashboard';
import UploadScan from '../pages/UploadScan';
import Prediction from '../pages/Prediction';
import Patients from '../pages/Patients';
import Reports from '../pages/Reports';
import Analytics from '../pages/Analytics';
import Emergency from '../pages/Emergency';
import Notifications from '../pages/Notifications';
import Settings from '../pages/Settings';
import NotFound from '../pages/NotFound';

const AppRoutes = () => {
  const { isAuthenticated } = useAuth();

  return (
    <ErrorBoundary>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
        <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} />
        
        {/* Protected Routes inside DashboardLayout */}
        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadScan />} />
          <Route path="/prediction/:predictionId" element={<Prediction />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/emergency" element={<Emergency />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
};

export default AppRoutes;
