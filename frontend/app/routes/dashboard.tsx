import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  Activity, AlertTriangle, Box, Brain, Clock,
  Factory, Layers, Lock, Eye, Play, Square, Check, RefreshCw
} from "lucide-react";
import { useDashboardStore } from "../../store/dashboard";
import { KpiCharts } from "../components/dashboard/kpi-charts";
import { PipelinePreview } from "../components/dashboard/pipeline-preview";
import { SlideOverPanel } from "../components/ui/slide-over-panel";
import { ProjectPanel, LinePanel, SimulationPanel, AlertPanel, SuggestionPanel, MachinePanel } from "../components/dashboard/detail-panels";
import type { Project, ProductionLine, Alert, Suggestion, Simulation, Machine, KPI } from "../../types/dashboard";
import { timeAgo } from "../../lib/utils";
// ✅ Import your Protect wrapper
import { Protect } from "~/features/auth/components/protect";

// ── Tiny helpers ────────────────────────────────────────

function StatusDot({ color }: { color: string }) {
  return (
    <span className="relative flex h-2 w-2">
      <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${color}`} />
      <span className={`relative inline-flex rounded-full h-2 w-2 ${color}`} />
    </span>
  );
}

// ── Main Dashboard ──────────────────────────────────────
export default function Dashboard() {
  const store = useDashboardStore();
  const {
    projects, lines, machines, simulations, alerts, suggestions, kpis, isLoading, error,
    fetchDashboardData, acknowledgeAlert, resolveAlert, startSimulation, stopSimulation,
    completeSimulation, applySuggestion
  } = store;

  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    projects: false,
    production: false,
    simulations: false,
    alerts: false,
    suggestions: false,
  });

  type PanelState = {
    type: "project" | "line" | "machine" | "simulation" | "alert" | "suggestion";
    id: string;
  };
  const [panelStack, setPanelStack] = useState<PanelState[]>([]);
  const activePanel = panelStack.length > 0 ? panelStack[panelStack.length - 1] : null;

  const openPanel = (type: PanelState["type"], id: string) => {
    setPanelStack(prev => [...prev, { type, id }]);
  };
  const closePanel = () => setPanelStack([]);
  const goBack = () => setPanelStack(prev => prev.slice(0, -1));

  const toggleExpand = (col: string) => {
    setExpanded(prev => ({ ...prev, [col]: !prev[col] }));
  };

  // ✅ Only keep the data-fetching effect — auth is now handled by <Protect>
  useEffect(() => {
    fetchDashboardData();
    const i = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(i);
  }, [fetchDashboardData]);

  // ✅ Keep the UNAUTHORIZED error redirect — this handles mid-session 401s
  //    returned by dashboard API calls (separate from initial auth)
  const openAlerts = alerts.filter(a => a.status === "OPEN").length;
  const runningSims = simulations.filter(s => s.status === "RUNNING").length;

  const visibleProjects = expanded.projects ? projects : projects.slice(0, 5);
  const visibleLines = expanded.production ? lines : lines.slice(0, 5);
  const visibleSimulations = expanded.simulations ? simulations : simulations.slice(0, 5);
  const visibleAlerts = expanded.alerts ? alerts : alerts.slice(0, 5);
  const visibleSuggestions = expanded.suggestions ? suggestions : suggestions.slice(0, 5);

  // ✅ Wrap the entire render in <Protect> — it handles the redirect + loading state
  return (
    <Protect>
      <div className="min-h-screen bg-black text-neutral-200 font-sans">
        {/* ── Top Bar ──────────────────────────────────────── */}
        <header className="sticky top-0 z-50 border-b border-neutral-800 bg-black/80 backdrop-blur-md">
          <div className="max-w-[1600px] mx-auto flex items-center justify-between h-12 px-5">
            <div className="flex items-center gap-3">
              <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-white tracking-tight">
                <Factory className="h-4 w-4 text-white" />
                indus.io
              </Link>
              <span className="text-neutral-700">/</span>
              <span className="text-sm text-neutral-400">Dashboard</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => fetchDashboardData()} className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors cursor-pointer">
                <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
                Sync
              </button>
              <Link to="/projects-management" className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors">
                <Layers className="h-3 w-3" />
                Projects
              </Link>
              <Link to="/pipeline-builder" className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-neutral-400 hover:text-white border border-neutral-800 rounded-md hover:border-neutral-700 transition-colors">
                Pipeline
              </Link>
            </div>
          </div>
        </header>

        <main className="max-w-[1600px] mx-auto px-5 py-6">
          {/* ── Stats Strip ────────────────────────────────── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-neutral-800 rounded-lg overflow-hidden mb-6">
            <StatCell label="Projects" value={projects.length} />
            <StatCell label="Production Lines" value={lines.length} />
            <StatCell label="Machines" value={machines.length} />
            <StatCell label="Open Alerts" value={openAlerts} alert={openAlerts > 0} />
          </div>

          {/* ── Charts & Pipeline Preview ────────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
            <div className="lg:col-span-2">
              <KpiCharts
                kpis={kpis}
                kpiValues={store.kpiValues}
                machines={machines}
                sensorData={store.sensorData}
              />
            </div>
            <div>
              <PipelinePreview machines={machines} connections={[]} />
            </div>
          </div>

          {/* ── Four Column Grid ───────────────────────────── */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

            {/* Column 1: Projects */}
            <Column title="Projects" count={projects.length} icon={<Layers className="h-3.5 w-3.5" />}>
              {isLoading && projects.length === 0 ? (
                <LoadingRows count={3} />
              ) : projects.length === 0 ? (
                <EmptyState text="No projects yet" />
              ) : (
                <div className="stagger-children space-y-2">
                  {visibleProjects.map(p => <ProjectCard key={p.id} project={p} lines={lines.filter(l => l.project_id === p.id)} onClick={() => openPanel("project", p.id)} />)}
                  {projects.length > 5 && (
                    <button
                      onClick={() => toggleExpand("projects")}
                      className="w-full py-2 text-[11px] font-semibold text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 rounded-lg hover:bg-neutral-950/80 transition-all cursor-pointer"
                    >
                      {expanded.projects ? "Show Less" : `Show More (${projects.length - 5} more)`}
                    </button>
                  )}
                </div>
              )}
            </Column>

            {/* Column 2: Production & Machines */}
            <Column title="Production" count={lines.length} icon={<Box className="h-3.5 w-3.5" />}>
              {isLoading && lines.length === 0 ? (
                <LoadingRows count={3} />
              ) : lines.length === 0 ? (
                <EmptyState text="No production lines" />
              ) : (
                <div className="stagger-children space-y-2">
                  {visibleLines.map(l => (
                    <LineCard key={l.id} line={l} machineCount={machines.filter(m => m.production_line_id === l.id).length} onClick={() => openPanel("line", l.id)} />
                  ))}
                  {lines.length > 5 && (
                    <button
                      onClick={() => toggleExpand("production")}
                      className="w-full py-2 text-[11px] font-semibold text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 rounded-lg hover:bg-neutral-950/80 transition-all cursor-pointer"
                    >
                      {expanded.production ? "Show Less" : `Show More (${lines.length - 5} more)`}
                    </button>
                  )}
                </div>
              )}
            </Column>

            {/* Column 3: Simulations & KPIs */}
            <Column title="Simulations" count={simulations.length} icon={<Activity className="h-3.5 w-3.5" />} badge={runningSims > 0 ? `${runningSims} running` : undefined}>
              {isLoading && simulations.length === 0 ? (
                <LoadingRows count={3} />
              ) : simulations.length === 0 ? (
                <EmptyState text="No simulations" />
              ) : (
                <div className="stagger-children space-y-2">
                  {visibleSimulations.map(s => (
                    <SimCard key={s.id} sim={s} onStart={() => startSimulation(s.id)} onStop={() => stopSimulation(s.id)} onComplete={() => completeSimulation(s.id)} onClick={() => openPanel("simulation", s.id)} />
                  ))}
                  {simulations.length > 5 && (
                    <button
                      onClick={() => toggleExpand("simulations")}
                      className="w-full py-2 text-[11px] font-semibold text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 rounded-lg hover:bg-neutral-950/80 transition-all cursor-pointer"
                    >
                      {expanded.simulations ? "Show Less" : `Show More (${simulations.length - 5} more)`}
                    </button>
                  )}
                </div>
              )}
            </Column>

            {/* Column 4: Alerts & AI */}
            <Column title="Intelligence" count={alerts.length + suggestions.length} icon={<Brain className="h-3.5 w-3.5" />} badge={openAlerts > 0 ? `${openAlerts} open` : undefined} badgeColor="text-red-400">
              {alerts.length > 0 && (
                <div className="space-y-1.5 mb-5">
                  <SectionLabel text="Alerts" />
                  <div className="stagger-children space-y-2">
                    {visibleAlerts.map(a => (
                      <AlertRow key={a.id} alert={a} onAck={() => acknowledgeAlert(a.id)} onResolve={() => resolveAlert(a.id)} onClick={() => openPanel("alert", a.id)} />
                    ))}
                    {alerts.length > 5 && (
                      <button
                        onClick={() => toggleExpand("alerts")}
                        className="w-full py-2 text-[11px] font-semibold text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 rounded-lg hover:bg-neutral-950/80 transition-all cursor-pointer"
                      >
                        {expanded.alerts ? "Show Less" : `Show More Alerts (${alerts.length - 5} more)`}
                      </button>
                    )}
                  </div>
                </div>
              )}
              {suggestions.length > 0 && (
                <div className="space-y-1.5">
                  <SectionLabel text="AI Suggestions" />
                  <div className="stagger-children space-y-2">
                    {visibleSuggestions.map(s => (
                      <SuggestionRow key={s.id} suggestion={s} onApply={() => applySuggestion(s.id)} onClick={() => openPanel("suggestion", s.id)} />
                    ))}
                    {suggestions.length > 5 && (
                      <button
                        onClick={() => toggleExpand("suggestions")}
                        className="w-full py-2 text-[11px] font-semibold text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 rounded-lg hover:bg-neutral-950/80 transition-all cursor-pointer"
                      >
                        {expanded.suggestions ? "Show Less" : `Show More Suggestions (${suggestions.length - 5} more)`}
                      </button>
                    )}
                  </div>
                </div>
              )}
              {alerts.length === 0 && suggestions.length === 0 && (
                isLoading ? <LoadingRows count={3} /> : <EmptyState text="All clear — no alerts" />
              )}
            </Column>
          </div>
        </main>

        {/* ── Slide Over Panel ─────────────────────────────────── */}
        <SlideOverPanel
          isOpen={activePanel !== null}
          onClose={closePanel}
          onBack={goBack}
          canGoBack={panelStack.length > 1}
          title={
            activePanel?.type === "project" ? "Project Details" :
              activePanel?.type === "line" ? "Production Line Details" :
                activePanel?.type === "machine" ? "Machine Details" :
                  activePanel?.type === "simulation" ? "Simulation Details" :
                    activePanel?.type === "alert" ? "Alert Details" :
                      activePanel?.type === "suggestion" ? "AI Suggestion" : ""
          }
          width="max-w-md"
        >
          {activePanel?.type === "project" && <ProjectPanel id={activePanel.id} openPanel={openPanel} />}
          {activePanel?.type === "line" && <LinePanel id={activePanel.id} openPanel={openPanel} />}
          {activePanel?.type === "machine" && <MachinePanel id={activePanel.id} openPanel={openPanel} />}
          {activePanel?.type === "simulation" && <SimulationPanel id={activePanel.id} openPanel={openPanel} />}
          {activePanel?.type === "alert" && <AlertPanel id={activePanel.id} openPanel={openPanel} />}
          {activePanel?.type === "suggestion" && <SuggestionPanel id={activePanel.id} openPanel={openPanel} />}
        </SlideOverPanel>
      </div>
    </Protect>
  );
}

// ── Sub-components ──────────────────────────────────────

function StatCell({ label, value, alert }: { label: string; value: number; alert?: boolean }) {
  return (
    <div className="bg-black px-4 py-3.5 flex flex-col gap-1">
      <span className="text-[11px] text-neutral-500 uppercase tracking-wider font-medium">{label}</span>
      <span className={`text-xl font-semibold tabular-nums ${alert ? "text-red-400" : "text-white"}`}>{value}</span>
    </div>
  );
}

function Column({ title, count, icon, badge, badgeColor, children }: { title: string; count: number; icon: React.ReactNode; badge?: string; badgeColor?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between mb-3 px-0.5">
        <div className="flex items-center gap-2 text-sm font-medium text-white">
          <span className="text-neutral-500">{icon}</span>
          {title}
          <span className="text-xs text-neutral-600 tabular-nums">{count}</span>
        </div>
        {badge && <span className={`text-[10px] font-medium ${badgeColor || "text-emerald-400"}`}>{badge}</span>}
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto max-h-[calc(100vh-200px)] pr-1">
        {children}
      </div>
    </div>
  );
}

function ProjectCard({ project, lines, onClick }: { project: Project; lines: ProductionLine[]; onClick?: () => void }) {
  const running = lines.filter(l => l.status === "RUNNING").length;
  return (
    <div onClick={onClick} className="group border border-neutral-800 rounded-lg p-3.5 hover:border-neutral-700 transition-all cursor-pointer bg-neutral-950/50">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-sm font-medium text-white truncate">{project.name}</span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {project.visibility === "PUBLIC" ? <Eye className="h-3 w-3 text-neutral-600" /> : <Lock className="h-3 w-3 text-neutral-600" />}
          <span className="text-[10px] text-neutral-600 uppercase">{project.visibility}</span>
        </div>
      </div>
      {project.description && <p className="text-xs text-neutral-500 mb-2.5 line-clamp-2">{project.description}</p>}
      <div className="flex items-center gap-3 text-[11px] text-neutral-500">
        <span className="flex items-center gap-1"><Layers className="h-3 w-3" />{lines.length} lines</span>
        {running > 0 && <span className="flex items-center gap-1"><StatusDot color="bg-emerald-500" />{running} active</span>}
        <span className="flex items-center gap-1 ml-auto"><Clock className="h-3 w-3" />{timeAgo(project.created_at)}</span>
      </div>
    </div>
  );
}

function LineCard({ line, machineCount, onClick }: { line: ProductionLine; machineCount: number; onClick?: () => void }) {
  const statusColor = line.status === "RUNNING" ? "bg-emerald-500" : line.status === "ARCHIVED" ? "bg-neutral-600" : "bg-amber-500";
  return (
    <div onClick={onClick} className="border border-neutral-800 rounded-lg p-3.5 hover:border-neutral-700 transition-all cursor-pointer bg-neutral-950/50">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-medium text-white truncate">{line.name}</span>
        <div className="flex items-center gap-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${statusColor}`} />
          <span className="text-[10px] text-neutral-500 uppercase">{line.status || "DRAFT"}</span>
        </div>
      </div>
      <div className="flex items-center gap-3 text-[11px] text-neutral-500">
        <span className="flex items-center gap-1"><Box className="h-3 w-3" />{machineCount} machines</span>
        <span className="flex items-center gap-1 ml-auto"><Clock className="h-3 w-3" />{timeAgo(line.updated_at)}</span>
      </div>
    </div>
  );
}

function SimCard({ sim, onStart, onStop, onComplete, onClick }: { sim: Simulation; onStart: () => void; onStop: () => void; onComplete: () => void; onClick?: () => void }) {
  const isRunning = sim.status === "RUNNING";
  const isStopped = sim.status === "STOPPED";
  const isDone = sim.status === "COMPLETED";
  return (
    <div onClick={onClick} className="border border-neutral-800 rounded-lg p-3.5 hover:border-neutral-700 transition-all cursor-pointer bg-neutral-950/50">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-mono text-neutral-400 truncate">{sim.id.slice(0, 8)}…</span>
        <div className="flex items-center gap-1.5">
          {isRunning && <StatusDot color="bg-emerald-500" />}
          <span className={`text-[10px] font-medium uppercase ${isRunning ? "text-emerald-400" : isDone ? "text-blue-400" : "text-neutral-500"}`}>{sim.status || "—"}</span>
        </div>
      </div>
      <div className="flex items-center gap-1.5">
        <button onClick={(e) => { e.stopPropagation(); onStart(); }} disabled={isRunning || isDone} className="flex items-center gap-1 px-2 py-1 text-[10px] border border-neutral-800 rounded hover:border-neutral-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer text-neutral-300 hover:text-white">
          <Play className="h-3 w-3" /> Start
        </button>
        <button onClick={(e) => { e.stopPropagation(); onStop(); }} disabled={!isRunning} className="flex items-center gap-1 px-2 py-1 text-[10px] border border-neutral-800 rounded hover:border-red-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer text-neutral-300 hover:text-red-400">
          <Square className="h-3 w-3" /> Stop
        </button>
        <button onClick={(e) => { e.stopPropagation(); onComplete(); }} disabled={isDone} className="flex items-center gap-1 px-2 py-1 text-[10px] border border-neutral-800 rounded hover:border-blue-800 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer text-neutral-300 hover:text-blue-400">
          <Check className="h-3 w-3" /> Complete
        </button>
      </div>
      <div className="flex items-center gap-3 text-[11px] text-neutral-600 mt-2">
        {sim.start_time && <span>Started {timeAgo(sim.start_time)}</span>}
        <span className="ml-auto">{timeAgo(sim.created_at)}</span>
      </div>
    </div>
  );
}

function AlertRow({ alert, onAck, onResolve, onClick }: { alert: Alert; onAck: () => void; onResolve: () => void; onClick?: () => void }) {
  const sevColor = alert.severity === "CRITICAL" ? "text-red-400" : alert.severity === "HIGH" ? "text-orange-400" : alert.severity === "MEDIUM" ? "text-amber-400" : "text-blue-400";
  const dotColor = alert.severity === "CRITICAL" ? "bg-red-500" : alert.severity === "HIGH" ? "bg-orange-500" : alert.severity === "MEDIUM" ? "bg-amber-500" : "bg-blue-500";
  return (
    <div onClick={onClick} className={`border border-neutral-800 rounded-lg p-3 hover:border-neutral-700 transition-all cursor-pointer bg-neutral-950/50 ${alert.status === "RESOLVED" ? "opacity-40" : ""}`}>
      <div className="flex items-start gap-2">
        <span className={`h-1.5 w-1.5 rounded-full mt-1.5 shrink-0 ${dotColor} ${alert.severity === "CRITICAL" ? "animate-pulse-dot" : ""}`} />
        <div className="flex-1 min-w-0">
          <p className="text-xs text-neutral-200 leading-relaxed">{alert.message}</p>
          <div className="flex items-center gap-2 mt-1.5">
            <span className={`text-[10px] font-medium uppercase ${sevColor}`}>{alert.severity}</span>
            <span className="text-[10px] text-neutral-600">·</span>
            <span className="text-[10px] text-neutral-600">{timeAgo(alert.created_at)}</span>
            {alert.status !== "RESOLVED" && (
              <div className="flex items-center gap-1 ml-auto">
                {!alert.acknowledged && <button onClick={(e) => { e.stopPropagation(); onAck(); }} className="text-[10px] text-amber-500 hover:text-amber-400 cursor-pointer">Ack</button>}
                {alert.acknowledged && <button onClick={(e) => { e.stopPropagation(); onResolve(); }} className="text-[10px] text-emerald-500 hover:text-emerald-400 cursor-pointer">Resolve</button>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SuggestionRow({ suggestion, onApply, onClick }: { suggestion: Suggestion; onApply?: () => void; onClick?: () => void }) {
  return (
    <div onClick={onClick} className="border border-neutral-800 rounded-lg p-3 hover:border-neutral-700 transition-all cursor-pointer bg-neutral-950/50">
      <p className="text-xs text-neutral-200 leading-relaxed mb-1.5">{suggestion.description}</p>
      <div className="flex items-center gap-2">
        {suggestion.type && <span className="text-[10px] text-neutral-500 border border-neutral-800 rounded px-1.5 py-0.5">{suggestion.type}</span>}
        {suggestion.confidence != null && (
          <div className="flex items-center gap-1.5">
            <div className="w-12 h-1 bg-neutral-800 rounded-full overflow-hidden">
              <div className="h-full bg-neutral-400 rounded-full" style={{ width: `${suggestion.confidence * 100}%` }} />
            </div>
            <span className="text-[10px] font-mono text-neutral-500">{Math.round(suggestion.confidence * 100)}%</span>
          </div>
        )}
        {!suggestion.applied && onApply && (
          <button onClick={(e) => { e.stopPropagation(); onApply(); }} className="text-[10px] text-emerald-500 hover:text-emerald-400 cursor-pointer ml-auto font-medium">Apply</button>
        )}
        {suggestion.applied && <span className="text-[10px] text-emerald-500 ml-auto font-medium">Applied</span>}
      </div>
    </div>
  );
}

function SectionLabel({ text }: { text: string }) {
  return <p className="text-[10px] uppercase tracking-widest text-neutral-600 font-medium px-0.5 mb-1">{text}</p>;
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="flex items-center justify-center py-12 text-xs text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
      {text}
    </div>
  );
}

function LoadingRows({ count }: { count: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-[72px] rounded-lg animate-shimmer" />
      ))}
    </div>
  );
}
