import axios, { type AxiosInstance } from 'axios';
import { useAuthStore } from '../features/auth/auth.store';

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
    const token = useAuthStore.getState().token;

    if (token) {
      request.headers.Authorization = `Bearer ${token}`;
    }

    return request;
  },
  (error) => Promise.reject(error)
);

export default api;

// ── System (public) ─────────────────────────────────────
export const systemService = {
  getStats: () =>
    api.get<{ projects: number; lines: number; machines: number; open_alerts: number }>(
      "/api/v1/system/stats"
    ),
};
