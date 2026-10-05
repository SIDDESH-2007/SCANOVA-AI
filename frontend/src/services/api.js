import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('hospital_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for clean error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      console.error('Backend offline or network error:', error);
      return Promise.reject({
        message: 'Backend server is offline or unreachable. Please ensure FastAPI server is running.',
        status: 0
      });
    }

    const { status, data } = error.response;
    const detailMessage = typeof data?.detail === 'string' ? data.detail : (data?.message || 'Request failed');

    if (status === 401) {
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('hospital_token');
        window.location.href = '/login';
      }
      return Promise.reject({ message: detailMessage || 'Invalid credentials or session expired.', status, response: error.response });
    } else if (status === 400 || status === 422) {
      return Promise.reject({ message: detailMessage || 'Invalid request parameters.', status, response: error.response });
    } else if (status === 500) {
      return Promise.reject({ message: detailMessage || 'Internal server error.', status, response: error.response });
    }

    return Promise.reject({ message: detailMessage || 'An unexpected error occurred.', status, response: error.response });
  }
);

export default api;
