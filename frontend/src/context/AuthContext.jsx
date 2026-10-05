import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = async () => {
    const token = localStorage.getItem('hospital_token');
    if (token) {
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch user:", error);
        localStorage.removeItem('hospital_token');
        setUser(null);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    loadUser();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      
      if (response.data.requiresTwoFactor) {
        return { requiresTwoFactor: true, userId: response.data.userId };
      }
      
      localStorage.setItem('hospital_token', response.data.access_token);
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      const detail = error.response?.data?.detail || error.message;
      if (Array.isArray(detail)) {
        throw new Error(detail[0]?.msg || "Validation error");
      }
      throw new Error(typeof detail === 'string' ? detail : "Login failed. Please check credentials.");
    }
  };

  const verifyLogin2FA = async (userId, token) => {
    try {
      const response = await api.post('/auth/2fa/verify-login', { userId, token });
      localStorage.setItem('hospital_token', response.data.access_token);
      setUser(response.data.user);
      return { success: true };
    } catch (error) {
      console.error("2FA verification error:", error);
      const detail = error.response?.data?.detail || error.message;
      throw new Error(typeof detail === 'string' ? detail : "Invalid 2FA code");
    }
  };

  const register = async (userData) => {
    try {
      await api.post('/auth/register', userData);
      return true;
    } catch (error) {
      console.error("Registration error:", error);
      const detail = error.response?.data?.detail || error.message;
      if (Array.isArray(detail)) {
        throw new Error(detail[0]?.msg || "Validation error");
      }
      throw new Error(typeof detail === 'string' ? detail : "Registration failed");
    }
  };

  const logout = () => {
    localStorage.removeItem('hospital_token');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    verifyLogin2FA,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
