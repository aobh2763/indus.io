import { create } from "zustand";
import type {
  Project,
  ProductionLine,
  Machine,
  Simulation,
  Alert,
  Suggestion,
  KPI,
  KPIValue,
  SensorData,
} from "../types/dashboard";
import {
  projectService,
  lineService,
  machineService,
  simulationService,
  alertService,
  suggestionService,
  kpiService,
  telemetryService,
} from "../lib/api";
import { useAuthStore } from "~/features/auth/auth.store";

interface DashboardState {
  // Data
  projects: Project[];
  lines: ProductionLine[];
  machines: Machine[];
  simulations: Simulation[];
  alerts: Alert[];
  suggestions: Suggestion[];
  kpis: KPI[];
  kpiValues: Record<string, KPIValue[]>;
  sensorData: Record<string, SensorData[]>;

  // UI State
  isLoading: boolean;
  error: string | null;
  selectedProjectId: string | null;
  selectedLineId: string | null;

  // Actions
  fetchDashboardData: () => Promise<void>;
  fetchProjectLines: (projectId: string) => Promise<void>;
  fetchLineMachines: (lineId: string) => Promise<void>;
  fetchLineSimulations: (lineId: string) => Promise<void>;
  fetchLineSuggestions: (lineId: string) => Promise<void>;
  fetchLineKpis: (lineId: string) => Promise<void>;
  fetchKpiValues: (kpiId: string) => Promise<void>;
  fetchMachineSensorData: (machineId: string) => Promise<void>;
  refreshAlerts: () => Promise<void>;
  acknowledgeAlert: (id: string) => Promise<void>;
  resolveAlert: (id: string) => Promise<void>;
  startSimulation: (id: string) => Promise<void>;
  stopSimulation: (id: string) => Promise<void>;
  completeSimulation: (id: string) => Promise<void>;
  applySuggestion: (id: string) => Promise<void>;
  setSelectedProject: (id: string | null) => void;
  setSelectedLine: (id: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  // Initial state
  projects: [],
  lines: [],
  machines: [],
  simulations: [],
  alerts: [],
  suggestions: [],
  kpis: [],
  kpiValues: {},
  sensorData: {},
  isLoading: false,
  error: null,
  selectedProjectId: null,
  selectedLineId: null,

  // ── Fetch all top-level dashboard data ─────────────────
  fetchDashboardData: async () => {
    set({ isLoading: true, error: null });
    try {
      const token = useAuthStore.getState().token;
      if (!token) {
        set({ error: "UNAUTHORIZED", isLoading: false });
        return;
      }

      const [projectsRes, alertsRes] = await Promise.all([
        projectService.list().catch((e) => {
          if (e.response?.status === 401) {
            set({ error: "UNAUTHORIZED" });
          }
          return { data: [] };
        }),
        alertService.list().catch(() => ({ data: [] })),
      ]);

      const projects = projectsRes.data || [];
      const alerts = alertsRes.data || [];

      // Fetch lines for all projects
      let allLines: ProductionLine[] = [];
      let allMachines: Machine[] = [];
      let allSimulations: Simulation[] = [];
      let allSuggestions: Suggestion[] = [];
      let allKpis: KPI[] = [];

      for (const project of projects) {
        try {
          const linesRes = await lineService.listByProject(project.id);
          allLines = [...allLines, ...linesRes.data];
        } catch { /* skip */ }
      }

      // Fetch machines, simulations, suggestions, KPIs for all lines
      for (const line of allLines) {
        try {
          const [machinesRes, simsRes, suggestionsRes, kpisRes] = await Promise.all([
            machineService.listByLine(line.id).catch(() => ({ data: [] })),
            simulationService.listByLine(line.id).catch(() => ({ data: [] })),
            suggestionService.listByLine(line.id).catch(() => ({ data: [] })),
            kpiService.listByLine(line.id).catch(() => ({ data: [] })),
          ]);
          allMachines = [...allMachines, ...machinesRes.data];
          allSimulations = [...allSimulations, ...simsRes.data];
          allSuggestions = [...allSuggestions, ...suggestionsRes.data];
          allKpis = [...allKpis, ...kpisRes.data];
        } catch { /* skip */ }
      }

      set({
        projects,
        alerts,
        lines: allLines,
        machines: allMachines,
        simulations: allSimulations,
        suggestions: allSuggestions,
        kpis: allKpis,
        isLoading: false,
      });
    } catch (err: any) {
      set({ error: err.message || "Failed to fetch dashboard data", isLoading: false });
    }
  },

  fetchProjectLines: async (projectId: string) => {
    try {
      const res = await lineService.listByProject(projectId);
      set({ lines: res.data });
    } catch { /* skip */ }
  },

  fetchLineMachines: async (lineId: string) => {
    try {
      const res = await machineService.listByLine(lineId);
      set({ machines: res.data });
    } catch { /* skip */ }
  },

  fetchLineSimulations: async (lineId: string) => {
    try {
      const res = await simulationService.listByLine(lineId);
      set({ simulations: res.data });
    } catch { /* skip */ }
  },

  fetchLineSuggestions: async (lineId: string) => {
    try {
      const res = await suggestionService.listByLine(lineId);
      set({ suggestions: res.data });
    } catch { /* skip */ }
  },

  fetchLineKpis: async (lineId: string) => {
    try {
      const res = await kpiService.listByLine(lineId);
      set({ kpis: res.data });
    } catch { /* skip */ }
  },

  fetchKpiValues: async (kpiId: string) => {
    try {
      const res = await kpiService.getValues(kpiId);
      set((state) => ({
        kpiValues: { ...state.kpiValues, [kpiId]: res.data },
      }));
    } catch { /* skip */ }
  },

  fetchMachineSensorData: async (machineId: string) => {
    try {
      const res = await telemetryService.listByMachine(machineId);
      set((state) => ({
        sensorData: { ...state.sensorData, [machineId]: res.data },
      }));
    } catch { /* skip */ }
  },

  refreshAlerts: async () => {
    try {
      const res = await alertService.list();
      set({ alerts: res.data });
    } catch { /* skip */ }
  },

  acknowledgeAlert: async (id: string) => {
    try {
      await alertService.acknowledge(id);
      const alerts = get().alerts.map((a) =>
        a.id === id ? { ...a, acknowledged: true, status: "IN_PROGRESS" as const } : a
      );
      set({ alerts });
    } catch { /* skip */ }
  },

  resolveAlert: async (id: string) => {
    try {
      await alertService.resolve(id);
      const alerts = get().alerts.map((a) =>
        a.id === id ? { ...a, status: "RESOLVED" as const, resolved_at: new Date().toISOString() } : a
      );
      set({ alerts });
    } catch { /* skip */ }
  },

  startSimulation: async (id: string) => {
    try {
      const res = await simulationService.start(id);
      const sims = get().simulations.map((s) =>
        s.id === id ? res.data : s
      );
      set({ simulations: sims });
    } catch { /* skip */ }
  },

  stopSimulation: async (id: string) => {
    try {
      const res = await simulationService.stop(id);
      const sims = get().simulations.map((s) =>
        s.id === id ? res.data : s
      );
      set({ simulations: sims });
    } catch { /* skip */ }
  },

  completeSimulation: async (id: string) => {
    try {
      const res = await simulationService.complete(id);
      const sims = get().simulations.map((s) =>
        s.id === id ? res.data : s
      );
      set({ simulations: sims });
    } catch { /* skip */ }
  },

  applySuggestion: async (id: string) => {
    try {
      const res = await suggestionService.update(id, { applied: true });
      const suggestions = get().suggestions.map((s) =>
        s.id === id ? res.data : s
      );
      set({ suggestions });
    } catch { /* skip */ }
  },

  setSelectedProject: (id) => set({ selectedProjectId: id }),
  setSelectedLine: (id) => set({ selectedLineId: id }),
}));
