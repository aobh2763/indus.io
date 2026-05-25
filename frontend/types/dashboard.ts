// ── Project ──────────────────────────────────────────────
export interface Project {
  id: string;
  name: string;
  description?: string;
  visibility: "PUBLIC" | "PRIVATE";
  created_at: string;
  updated_at: string;
}

// ── Production Line ─────────────────────────────────────
export interface ProductionLine {
  id: string;
  project_id: string;
  name: string;
  status?: "DRAFT" | "RUNNING" | "ARCHIVED";
  created_at: string;
  updated_at: string;
}

// ── Machine ─────────────────────────────────────────────
export interface Machine {
  id: string;
  production_line_id: string;
  name: string;
  process?: string;
  subprocess?: string;
  manufacturer?: string;
  model_reference?: string;
  year_introduced?: number;
  description?: string;
  icon?: string;
  position_x: number;
  position_y: number;
  parameters?: Record<string, any>;
  is_configured: boolean;
  created_at: string;
  updated_at: string;
}

// ── Connection ──────────────────────────────────────────
export interface Connection {
  id: string;
  production_line_id: string;
  source_machine_id: string;
  target_machine_id: string;
  weight: number;
  created_at: string;
}

// ── Simulation ──────────────────────────────────────────
export interface Simulation {
  id: string;
  production_line_id: string;
  status?: "RUNNING" | "STOPPED" | "COMPLETED";
  start_time?: string;
  end_time?: string;
  created_at: string;
}

export interface SimulationLog {
  id: string;
  simulation_id: string;
  machine_id?: string;
  level?: "INFO" | "WARNING" | "ERROR";
  message?: string;
  created_at: string;
}

// ── KPI ─────────────────────────────────────────────────
export interface KPI {
  id: string;
  production_line_id: string;
  machine_id?: string;
  name: string;
  formula?: string;
  target_value?: number;
  unit?: string;
  created_at: string;
  updated_at: string;
}

export interface KPIValue {
  id: string;
  kpi_id: string;
  simulation_id?: string;
  value: number;
  timestamp: string;
}

// ── Telemetry ───────────────────────────────────────────
export interface SensorData {
  id: string;
  machine_id: string;
  type: string;
  value: number;
  source?: string;
  quality_score?: number;
  timestamp: string;
}

// ── AI Agent ────────────────────────────────────────────
export interface AIAgent {
  id: string;
  name: string;
  type: string;
  version?: string;
  created_at: string;
}

// ── Suggestion ──────────────────────────────────────────
export interface Suggestion {
  id: string;
  ai_agent_id?: string;
  production_line_id: string;
  machine_id?: string;
  type?: string;
  description?: string;
  payload?: Record<string, any>;
  confidence?: number;
  applied: boolean;
  created_at: string;
}

// ── Alert ───────────────────────────────────────────────
export interface Alert {
  id: string;
  production_line_id: string;
  machine_id?: string;
  kpi_id?: string;
  simulation_id?: string;
  type: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  message: string;
  status: "OPEN" | "IN_PROGRESS" | "RESOLVED";
  acknowledged: boolean;
  created_at: string;
  resolved_at?: string;
}

// ── Auth ────────────────────────────────────────────────
export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
