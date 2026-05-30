import axios, { type AxiosInstance } from 'axios';

export const API_PREFIX = '/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

api.interceptors.request.use(
  (request) => {
    const { useAuthStore } = require('../features/auth/auth.store');
    const token = useAuthStore.getState().token;

    if (token) {
      request.headers.Authorization = `Bearer ${token}`;
    }

    return request;
  },
  (error) => Promise.reject(error)
);

export default api;