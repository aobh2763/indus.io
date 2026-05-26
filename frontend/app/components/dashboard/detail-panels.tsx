import { Layers, Lock, Eye, Clock, Box, Play, Square, Check, Activity, AlertTriangle, Brain } from "lucide-react";
import { useDashboardStore } from "../../../store/dashboard";
import { timeAgo } from "../../../lib/utils";

// ── Project Panel ───────────────────────────────────────
export function ProjectPanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { projects, lines } = useDashboardStore();
  const project = projects.find(p => p.id === id);
  if (!project) return <div>Project not found</div>;

  const projectLines = lines.filter(l => l.project_id === id);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          {project.visibility === "PUBLIC" ? <Eye className="h-4 w-4 text-neutral-500" /> : <Lock className="h-4 w-4 text-neutral-500" />}
          <span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{project.visibility}</span>
        </div>
        <h3 className="text-2xl font-semibold text-white tracking-tight">{project.name}</h3>
        {project.description && <p className="text-sm text-neutral-400 mt-2 leading-relaxed">{project.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Created</p>
          <p className="text-xs text-neutral-300">{timeAgo(project.created_at)}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Last Updated</p>
          <p className="text-xs text-neutral-300">{timeAgo(project.updated_at)}</p>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-white flex items-center gap-2">
            <Layers className="h-4 w-4 text-neutral-400" />
            Production Lines ({projectLines.length})
          </h4>
        </div>
        <div className="space-y-2">
          {projectLines.length === 0 ? (
            <div className="text-xs text-neutral-500 border border-dashed border-neutral-800 rounded-lg p-4 text-center">No production lines in this project</div>
          ) : (
            projectLines.map(line => (
              <div
                key={line.id}
                onClick={() => openPanel("line", line.id)}
                className="flex items-center justify-between p-3 border border-neutral-800 rounded-lg bg-neutral-950/50 hover:bg-neutral-900 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${line.status === "RUNNING" ? "bg-emerald-500" : line.status === "ARCHIVED" ? "bg-neutral-600" : "bg-amber-500"}`} />
                  <span className="text-sm text-neutral-200">{line.name}</span>
                </div>
                <span className="text-[10px] text-neutral-500 uppercase">{line.status || "DRAFT"}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ── Line Panel ──────────────────────────────────────────
export function LinePanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { lines, machines, projects, simulations, suggestions, kpis } = useDashboardStore();
  const line = lines.find(l => l.id === id);
  if (!line) return <div>Line not found</div>;

  const project = projects.find(p => p.id === line.project_id);
  const lineMachines = machines.filter(m => m.production_line_id === id);
  const lineSims = simulations.filter(s => s.production_line_id === id);
  const lineKpis = kpis.filter(k => k.production_line_id === id);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className={`h-2 w-2 rounded-full ${line.status === "RUNNING" ? "bg-emerald-500" : line.status === "ARCHIVED" ? "bg-neutral-600" : "bg-amber-500"}`} />
          <span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{line.status || "DRAFT"}</span>
          <span className="text-neutral-700 mx-1">•</span>
          <span className="text-xs text-neutral-400 cursor-pointer hover:text-white transition-colors" onClick={() => project && openPanel("project", project.id)}>{project?.name || "Unknown Project"}</span>
        </div>
        <h3 className="text-2xl font-semibold text-white tracking-tight">{line.name}</h3>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white flex items-center gap-2 mb-3">
          <Box className="h-4 w-4 text-neutral-400" />
          Machines ({lineMachines.length})
        </h4>
        <div className="grid grid-cols-1 gap-2">
          {lineMachines.length === 0 ? (
            <div className="text-xs text-neutral-500 border border-dashed border-neutral-800 rounded-lg p-4 text-center">No machines assigned</div>
          ) : (
            lineMachines.map(m => (
              <div
                key={m.id}
                onClick={() => openPanel("machine", m.id)}
                className="p-3 border border-neutral-800 rounded-lg bg-neutral-950/50 cursor-pointer hover:bg-neutral-900 transition-colors"
              >
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-neutral-200 font-medium">{m.name}</span>
                  <span className="text-[10px] text-neutral-500 border border-neutral-800 rounded px-1.5 py-0.5">{m.process || "Unknown"}</span>
                </div>
                <p className="text-[11px] text-neutral-500">{m.manufacturer || "Unknown Make"} • {m.model_reference || "No Model"}</p>
              </div>
            ))
          )}
        </div>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white flex items-center gap-2 mb-3">
          <Activity className="h-4 w-4 text-neutral-400" />
          KPIs ({lineKpis.length})
        </h4>
        <div className="grid grid-cols-1 gap-2">
          {lineKpis.length === 0 ? (
            <div className="text-xs text-neutral-500 border border-dashed border-neutral-800 rounded-lg p-4 text-center">No KPIs defined</div>
          ) : (
            lineKpis.map(k => (
              <div key={k.id} className="p-3 border border-neutral-800 rounded-lg bg-neutral-950/50 flex items-center justify-between">
                <div>
                  <span className="text-sm text-neutral-200 font-medium">{k.name}</span>
                  {k.target_value && <p className="text-[11px] text-neutral-500">Target: {k.target_value} {k.unit}</p>}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

// ── Machine Panel ───────────────────────────────────────
export function MachinePanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { machines, lines } = useDashboardStore();
  const machine = machines.find(m => m.id === id);
  if (!machine) return <div>Machine not found</div>;

  const line = lines.find(l => l.id === machine.production_line_id);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{machine.process || "Machine"}</span>
          <span className="text-neutral-700 mx-1">•</span>
          <span className="text-xs text-neutral-400 cursor-pointer hover:text-white transition-colors" onClick={() => line && openPanel("line", line.id)}>{line?.name || "Unknown Line"}</span>
        </div>
        <h3 className="text-2xl font-semibold text-white tracking-tight">{machine.name}</h3>
        {machine.description && <p className="text-sm text-neutral-400 mt-2 leading-relaxed">{machine.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Manufacturer</p>
          <p className="text-sm text-neutral-300">{machine.manufacturer || "—"}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Model Ref</p>
          <p className="text-sm font-mono text-neutral-300">{machine.model_reference || "—"}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Subprocess</p>
          <p className="text-sm text-neutral-300">{machine.subprocess || "—"}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Configured</p>
          <p className="text-sm text-neutral-300">{machine.is_configured ? "Yes" : "No"}</p>
        </div>
      </div>

      {machine.parameters && Object.keys(machine.parameters).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-white mb-2">Parameters</h4>
          <pre className="bg-neutral-950 border border-neutral-800 rounded-lg p-4 text-[11px] font-mono text-blue-400 overflow-x-auto">
            {JSON.stringify(machine.parameters, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

// ── Simulation Panel ────────────────────────────────────
export function SimulationPanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { simulations, lines, startSimulation, stopSimulation, completeSimulation } = useDashboardStore();
  const sim = simulations.find(s => s.id === id);
  if (!sim) return <div>Simulation not found</div>;

  const line = lines.find(l => l.id === sim.production_line_id);
  const isRunning = sim.status === "RUNNING";
  const isDone = sim.status === "COMPLETED";

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Activity className="h-4 w-4 text-neutral-500" />
          <span className={`text-xs font-medium uppercase tracking-wider ${isRunning ? "text-emerald-400" : isDone ? "text-blue-400" : "text-neutral-500"}`}>{sim.status || "PENDING"}</span>
          <span className="text-neutral-700 mx-1">•</span>
          <span className="text-xs text-neutral-400 cursor-pointer hover:text-white transition-colors" onClick={() => line && openPanel("line", line.id)}>{line?.name || "Unknown Line"}</span>
        </div>
        <h3 className="text-2xl font-semibold text-white tracking-tight font-mono">{sim.id}</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Started</p>
          <p className="text-xs text-neutral-300">{timeAgo(sim.start_time)}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Ended</p>
          <p className="text-xs text-neutral-300">{timeAgo(sim.end_time)}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 p-4 bg-neutral-900 border border-neutral-800 rounded-lg">
        <button onClick={() => startSimulation(sim.id)} disabled={isRunning || isDone} className="flex-1 flex justify-center items-center gap-2 px-3 py-2 text-xs font-medium border border-neutral-700 bg-neutral-800 rounded-md hover:border-emerald-500/50 hover:text-emerald-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-white">
          <Play className="h-4 w-4" /> Start
        </button>
        <button onClick={() => stopSimulation(sim.id)} disabled={!isRunning} className="flex-1 flex justify-center items-center gap-2 px-3 py-2 text-xs font-medium border border-neutral-700 bg-neutral-800 rounded-md hover:border-red-500/50 hover:text-red-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-white">
          <Square className="h-4 w-4" /> Stop
        </button>
        <button onClick={() => completeSimulation(sim.id)} disabled={isDone} className="flex-1 flex justify-center items-center gap-2 px-3 py-2 text-xs font-medium border border-neutral-700 bg-neutral-800 rounded-md hover:border-blue-500/50 hover:text-blue-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-white">
          <Check className="h-4 w-4" /> Complete
        </button>
      </div>

      <div>
        <h4 className="text-sm font-medium text-white mb-3">Simulation Logs</h4>
        <div className="text-xs text-neutral-500 border border-dashed border-neutral-800 rounded-lg p-4 text-center">
          Log viewer coming soon...
        </div>
      </div>
    </div>
  );
}

// ── Alert Panel ─────────────────────────────────────────
export function AlertPanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { alerts, lines, acknowledgeAlert, resolveAlert } = useDashboardStore();
  const alert = alerts.find(a => a.id === id);
  if (!alert) return <div>Alert not found</div>;

  const line = lines.find(l => l.id === alert.production_line_id);
  const sevColor = alert.severity === "CRITICAL" ? "text-red-400" : alert.severity === "HIGH" ? "text-orange-400" : alert.severity === "MEDIUM" ? "text-amber-400" : "text-blue-400";
  const dotColor = alert.severity === "CRITICAL" ? "bg-red-500" : alert.severity === "HIGH" ? "bg-orange-500" : alert.severity === "MEDIUM" ? "bg-amber-500" : "bg-blue-500";

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className={`h-4 w-4 ${sevColor}`} />
          <span className={`text-xs font-medium uppercase tracking-wider ${sevColor}`}>{alert.severity}</span>
          <span className="text-neutral-700 mx-1">•</span>
          <span className="text-xs text-neutral-500 uppercase tracking-wider">{alert.status}</span>
        </div>
        <h3 className="text-xl font-semibold text-white tracking-tight leading-relaxed">{alert.message}</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Created</p>
          <p className="text-xs text-neutral-300">{timeAgo(alert.created_at)}</p>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Resolved</p>
          <p className="text-xs text-neutral-300">{timeAgo(alert.resolved_at)}</p>
        </div>
      </div>

      <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 space-y-3">
        <h4 className="text-sm font-medium text-white border-b border-neutral-800 pb-2">Context</h4>
        <div className="grid grid-cols-2 gap-y-3">
          <div>
            <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Production Line</p>
            <p className="text-sm text-neutral-300 cursor-pointer hover:text-white transition-colors" onClick={() => line && openPanel("line", line.id)}>{line?.name || "Unknown"}</p>
          </div>
          {alert.machine_id && (
            <div>
              <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Machine ID</p>
              <p className="text-sm font-mono text-neutral-300">{alert.machine_id.slice(0, 8)}…</p>
            </div>
          )}
        </div>
      </div>

      {alert.status !== "RESOLVED" && (
        <div className="flex items-center gap-3 pt-4 border-t border-neutral-800">
          {!alert.acknowledged && (
            <button onClick={() => acknowledgeAlert(alert.id)} className="flex-1 bg-amber-500 hover:bg-amber-600 text-amber-950 font-semibold text-sm py-2 rounded-md transition-colors">
              Acknowledge Alert
            </button>
          )}
          {alert.acknowledged && (
            <button onClick={() => resolveAlert(alert.id)} className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-emerald-950 font-semibold text-sm py-2 rounded-md transition-colors">
              Mark as Resolved
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ── Suggestion Panel ────────────────────────────────────
export function SuggestionPanel({ id, openPanel }: { id: string; openPanel: (type: any, id: string) => void }) {
  const { suggestions, lines, applySuggestion } = useDashboardStore();
  const suggestion = suggestions.find(s => s.id === id);
  if (!suggestion) return <div>Suggestion not found</div>;

  const line = lines.find(l => l.id === suggestion.production_line_id);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Brain className="h-4 w-4 text-emerald-500" />
          <span className="text-xs font-medium uppercase tracking-wider text-emerald-500">{suggestion.type || "AI AGENT"}</span>
        </div>
        <h3 className="text-xl font-semibold text-white tracking-tight leading-relaxed">{suggestion.description}</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Confidence</p>
          <div className="flex items-center gap-2 mt-1.5">
            <div className="flex-1 h-1.5 bg-neutral-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(suggestion.confidence || 0) * 100}%` }} />
            </div>
            <span className="text-xs font-mono text-emerald-400">{Math.round((suggestion.confidence || 0) * 100)}%</span>
          </div>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-3">
          <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Status</p>
          <p className={`text-xs font-medium uppercase ${suggestion.applied ? "text-emerald-400" : "text-neutral-300"}`}>
            {suggestion.applied ? "Applied" : "Pending Action"}
          </p>
        </div>
      </div>

      <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-4 space-y-3">
        <h4 className="text-sm font-medium text-white border-b border-neutral-800 pb-2">Target Scope</h4>
        <div className="grid grid-cols-2 gap-y-3">
          <div>
            <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Production Line</p>
            <p className="text-sm text-neutral-300 cursor-pointer hover:text-white transition-colors" onClick={() => line && openPanel("line", line.id)}>{line?.name || "Unknown"}</p>
          </div>
          {suggestion.machine_id && (
            <div>
              <p className="text-[10px] uppercase text-neutral-500 font-medium mb-1">Machine ID</p>
              <p className="text-sm font-mono text-neutral-300">{suggestion.machine_id.slice(0, 8)}…</p>
            </div>
          )}
        </div>
      </div>

      {suggestion.payload && Object.keys(suggestion.payload).length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-white mb-2">Parameter Adjustments</h4>
          <pre className="bg-neutral-950 border border-neutral-800 rounded-lg p-4 text-[11px] font-mono text-emerald-400 overflow-x-auto">
            {JSON.stringify(suggestion.payload, null, 2)}
          </pre>
        </div>
      )}

      {!suggestion.applied && (
        <div className="pt-4 border-t border-neutral-800">
          <button onClick={() => applySuggestion(suggestion.id)} className="w-full bg-emerald-500 hover:bg-emerald-600 text-emerald-950 font-semibold text-sm py-2 rounded-md transition-colors flex justify-center items-center gap-2">
            <Check className="h-4 w-4" /> Apply Optimization
          </button>
        </div>
      )}
    </div>
  );
}
