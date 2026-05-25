import axios, { type AxiosInstance } from 'axios';
import { useAuthStore } from '../features/auth/auth.store';

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:3000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

api.interceptors.request.use(
  (request) => {
    const token = useAuthStore.getState().token;

    if (token) {
      request.headers.Authorization = `Bearer ${token}`;
    }

    return request;
  },
  (error) => Promise.reject(error)
);

export default api;
