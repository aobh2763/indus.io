import axios from "axios";
import type {
  Project,
  ProductionLine,
  Machine,
  Connection,
  Simulation,
  SimulationLog,
  KPI,
  KPIValue,
  SensorData,
  AIAgent,
  Suggestion,
  Alert,
  User,
  TokenResponse,
} from "../types/dashboard";
import { useAuthStore } from "~/features/auth/auth.store";

// ── Axios Instance ──────────────────────────────────────
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Add auth token to requests
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

// ── Auth ────────────────────────────────────────────────
export const authService = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { email, password }),
  register: (name: string, email: string, password: string) =>
    api.post<User>("/auth/register", { name, email, password }),
};

// ── Users ───────────────────────────────────────────────
export const userService = {
  me: () => api.get<User>("/users/me"),
  list: (skip = 0, limit = 100) =>
    api.get<User[]>("/users", { params: { skip, limit } }),
};

// ── Projects ────────────────────────────────────────────
export const projectService = {
  list: (skip = 0, limit = 100) => {
    const res = api.get<Project[]>("/projects/", { params: { skip, limit } });
    console.log('list.res: ', res);
    return res;
  },
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: { name: string; description?: string; visibility?: string }) =>
    api.post<Project>("/projects/", data),
  update: (id: string, data: Partial<Project>) =>
    api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

// ── Production Lines ────────────────────────────────────
export const lineService = {
  listByProject: (projectId: string) =>
    api.get<ProductionLine[]>(`/projects/${projectId}/lines`),
  get: (id: string) => api.get<ProductionLine>(`/lines/${id}`),
  create: (projectId: string, data: { name: string; status?: string }) =>
    api.post<ProductionLine>(`/projects/${projectId}/lines`, data),
  update: (id: string, data: Partial<ProductionLine>) =>
    api.put<ProductionLine>(`/lines/${id}`, data),
  delete: (id: string) => api.delete(`/lines/${id}`),
};

// ── Machines ────────────────────────────────────────────
export const machineService = {
  listByLine: (lineId: string) =>
    api.get<Machine[]>(`/lines/${lineId}/machines`),
  get: (id: string) => api.get<Machine>(`/machines/${id}`),
  create: (lineId: string, data: any) =>
    api.post<Machine>(`/lines/${lineId}/machines`, data),
  update: (id: string, data: any) =>
    api.put<Machine>(`/machines/${id}`, data),
  delete: (id: string) => api.delete(`/machines/${id}`),
};

// ── Connections ─────────────────────────────────────────
export const connectionService = {
  listByLine: (lineId: string) =>
    api.get<Connection[]>(`/lines/${lineId}/connections`),
  get: (id: string) => api.get<Connection>(`/connections/${id}`),
  create: (lineId: string, data: any) =>
    api.post<Connection>(`/lines/${lineId}/connections`, data),
  delete: (id: string) => api.delete(`/connections/${id}`),
};

// ── Simulations ─────────────────────────────────────────
export const simulationService = {
  listByLine: (lineId: string) =>
    api.get<Simulation[]>(`/lines/${lineId}/simulations`),
  get: (id: string) => api.get<Simulation>(`/simulations/${id}`),
  create: (lineId: string, data?: any) =>
    api.post<Simulation>(`/lines/${lineId}/simulations`, data || {}),
  start: (id: string) => api.post<Simulation>(`/simulations/${id}/start`),
  stop: (id: string) => api.post<Simulation>(`/simulations/${id}/stop`),
  complete: (id: string) =>
    api.post<Simulation>(`/simulations/${id}/complete`),
  delete: (id: string) => api.delete(`/simulations/${id}`),
  // Logs
  getLogs: (simId: string) =>
    api.get<SimulationLog[]>(`/simulations/${simId}/logs`),
  createLog: (simId: string, data: any) =>
    api.post<SimulationLog>(`/simulations/${simId}/logs`, data),
};

// ── KPIs ────────────────────────────────────────────────
export const kpiService = {
  listByLine: (lineId: string) =>
    api.get<KPI[]>(`/lines/${lineId}/kpis`),
  get: (id: string) => api.get<KPI>(`/kpis/${id}`),
  create: (lineId: string, data: any) =>
    api.post<KPI>(`/lines/${lineId}/kpis`, data),
  update: (id: string, data: any) => api.put<KPI>(`/kpis/${id}`, data),
  delete: (id: string) => api.delete(`/kpis/${id}`),
  // Values
  getValues: (kpiId: string) =>
    api.get<KPIValue[]>(`/kpis/${kpiId}/values`),
  createValue: (kpiId: string, data: { value: number; simulation_id?: string }) =>
    api.post<KPIValue>(`/kpis/${kpiId}/values`, data),
};

// ── Telemetry ───────────────────────────────────────────
export const telemetryService = {
  listByMachine: (machineId: string, limit = 100) =>
    api.get<SensorData[]>(`/machines/${machineId}/sensor-data`, {
      params: { limit },
    }),
  create: (machineId: string, data: any) =>
    api.post<SensorData>(`/machines/${machineId}/sensor-data`, data),
  bulkCreate: (machineId: string, data: any[]) =>
    api.post<SensorData[]>(`/machines/${machineId}/sensor-data/bulk`, data),
};

// ── AI Agents ───────────────────────────────────────────
export const aiAgentService = {
  list: () => api.get<AIAgent[]>("/ai-agents"),
  get: (id: string) => api.get<AIAgent>(`/ai-agents/${id}`),
  create: (data: { name: string; type: string; version?: string }) =>
    api.post<AIAgent>("/ai-agents", data),
  update: (id: string, data: any) =>
    api.put<AIAgent>(`/ai-agents/${id}`, data),
  delete: (id: string) => api.delete(`/ai-agents/${id}`),
};

// ── Suggestions ─────────────────────────────────────────
export const suggestionService = {
  listByLine: (lineId: string) =>
    api.get<Suggestion[]>(`/lines/${lineId}/suggestions`),
  get: (id: string) => api.get<Suggestion>(`/suggestions/${id}`),
  create: (lineId: string, data: any) =>
    api.post<Suggestion>(`/lines/${lineId}/suggestions`, data),
  update: (id: string, data: { applied?: boolean }) =>
    api.put<Suggestion>(`/suggestions/${id}`, data),
};

// ── Alerts ──────────────────────────────────────────────
export const alertService = {
  list: (skip = 0, limit = 100) =>
    api.get<Alert[]>("/alerts/", { params: { skip, limit } }),
  get: (id: string) => api.get<Alert>(`/alerts/${id}`),
  create: (data: any) => api.post<Alert>("/alerts/", data),
  update: (id: string, data: any) => api.put<Alert>(`/alerts/${id}`, data),
  acknowledge: (id: string) =>
    api.post<Alert>(`/alerts/${id}/acknowledge`),
  resolve: (id: string) => api.post<Alert>(`/alerts/${id}/resolve`),
};

export default api;
