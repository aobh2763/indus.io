import { Link } from "react-router";
import {
  Factory,
  Activity,
  Box,
  Brain,
  Camera,
  ChevronRight,
  Layers,
  ScanLine,
  Workflow,
  BarChart3,
  Shield,
  Zap,
  ArrowRight,
} from "lucide-react";
import { useNavigate } from "react-router";

import { useEffect, useState } from "react";
import { useAuthStore } from "~/features/auth/auth.store";
import { systemService } from "~/lib/api";
import Navbar from "~/components/navbar";

export default function LandingPage() {
  const { isAuthenticated, isHydrated } = useAuthStore();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    projects: 12,
    lines: 34,
    machines: 89,
    open_alerts: 3,
  });

  useEffect(() => {
    systemService.getStats().then((res) => {
      setStats(res.data);
    }).catch(() => {
      // Ignore errors and keep defaults if backend is unreachable
    });
  }, []);

  // Redirect removed: authenticated users can still see the landing page

  return (
    <div className="min-h-screen bg-black text-neutral-200 selection:bg-emerald-500/30">
      {/* ── Navbar ──────────────────────────────────────── */}
      {isHydrated && isAuthenticated ? (
        <Navbar />
      ) : (
        <header className="sticky top-0 z-50 border-b border-neutral-800/60 bg-black/75 backdrop-blur-xl">
          <div className="max-w-[1200px] mx-auto flex items-center justify-between h-12 px-5">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="flex items-center justify-center w-[26px] h-[26px] rounded-[6px]">
                <Factory className="h-3.5 w-3.5" />
              </div>
              <span className="text-[13px] font-medium text-white tracking-tight">
                indus.io
              </span>
            </Link>
            <div className="flex items-center gap-1.5">
              <Link
                to="/login"
                className="px-3 py-1.5 text-[12px] text-neutral-400 hover:text-white transition-colors"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="px-3 py-1.5 text-[12px] font-medium text-black bg-white hover:bg-neutral-200 rounded-[7px] transition-colors"
              >
                Get started
              </Link>
            </div>
          </div>
        </header>
      )}

      {/* ── Hero ──────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Subtle grid background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px]" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black" />

        <div className="relative max-w-[1200px] mx-auto px-5 pt-24 pb-20">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2 mb-6">
              <span className="flex items-center gap-1.5 text-[11px] font-medium text-emerald-400 uppercase tracking-wider">
                <Activity className="h-3 w-3" />
                Production intelligence platform
              </span>
            </div>

            <h1 className="text-4xl md:text-5xl font-semibold text-white tracking-tight leading-[1.1] mb-5">
              Your textile factory,
              <br />
              <span className="text-neutral-500">one dashboard away.</span>
            </h1>

            <p className="text-base text-neutral-500 leading-relaxed max-w-lg mb-8">
              Model production lines, run simulations before committing resources,
              and catch quality defects in real time with AI-powered inspection.
              Built for textile operations teams.
            </p>

            <div className="flex items-center gap-3">
              {isHydrated && isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-black bg-white hover:bg-neutral-200 rounded-[8px] transition-colors"
                >
                  Go to Dashboard
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-black bg-white hover:bg-neutral-200 rounded-[8px] transition-colors"
                  >
                    Start for free
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                  <Link
                    to="/login"
                    className="flex items-center gap-2 px-4 py-2.5 text-sm text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 rounded-[8px] transition-colors"
                  >
                    Sign in
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Hero visual: simplified dashboard preview */}
          <div className="mt-16 rounded-xl border border-neutral-800 bg-neutral-950/80 overflow-hidden shadow-2xl shadow-black/50">
            <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-neutral-800/60 bg-neutral-950">
              <span className="h-2 w-2 rounded-full bg-neutral-700" />
              <span className="h-2 w-2 rounded-full bg-neutral-700" />
              <span className="h-2 w-2 rounded-full bg-neutral-700" />
              <span className="ml-3 text-[11px] text-neutral-600">indus.io — Dashboard</span>
            </div>
            <div className="p-5">
              {/* Stat strip */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-neutral-800 rounded-lg overflow-hidden mb-5">
                {[
                  { label: "Projects", value: stats.projects },
                  { label: "Production Lines", value: stats.lines },
                  { label: "Machines", value: stats.machines },
                  { label: "Open Alerts", value: stats.open_alerts },
                ].map((s) => (
                  <div key={s.label} className="bg-neutral-950 px-4 py-3 flex flex-col gap-1">
                    <span className="text-[10px] text-neutral-600 uppercase tracking-wider font-medium">
                      {s.label}
                    </span>
                    <span className="text-lg font-semibold tabular-nums text-neutral-300">
                      {s.value}
                    </span>
                  </div>
                ))}
              </div>

              {/* Fake chart area */}
              {/*
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2 h-32 rounded-lg border border-neutral-800 bg-black/40 flex items-end px-4 pb-3 gap-1.5">
                  {[40, 55, 38, 62, 45, 70, 58, 72, 65, 80, 68, 85, 75, 90, 82, 88].map((h, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-neutral-800 rounded-sm transition-all"
                      style={{ height: `${h}%` }}
                    />
                  ))}
                </div>
                <div className="h-32 rounded-lg border border-neutral-800 bg-black/40 p-3 flex flex-col justify-between">
                  <span className="text-[10px] text-neutral-600 uppercase tracking-wider">Pipeline</span>
                  <div className="flex items-center gap-2">
                    <div className="h-6 w-6 rounded bg-neutral-800" />
                    <div className="h-px flex-1 bg-neutral-800" />
                    <div className="h-6 w-6 rounded bg-neutral-800" />
                    <div className="h-px flex-1 bg-neutral-800" />
                    <div className="h-6 w-6 rounded bg-neutral-800" />
                  </div>
                  <div className="flex gap-1">
                    <span className="h-1.5 flex-1 rounded-full bg-emerald-500/30" />
                    <span className="h-1.5 flex-1 rounded-full bg-emerald-500/20" />
                    <span className="h-1.5 flex-1 rounded-full bg-neutral-800" />
                  </div>
                </div>
              </div>
              */}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────── */}
      <section className="max-w-[1200px] mx-auto px-5 py-20">
        <div className="mb-12">
          <p className="text-[11px] font-medium text-neutral-600 uppercase tracking-wider mb-2">
            What you get
          </p>
          <h2 className="text-2xl font-semibold text-white tracking-tight">
            Everything to run a smarter line
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FeatureCard
            icon={<Workflow className="h-4 w-4" />}
            title="Pipeline builder"
            description="Drag-and-drop production line modelling. Wire up machines, define flows, and edit your configurations."
          />
          <FeatureCard
            icon={<Activity className="h-4 w-4" />}
            title="Simulation engine"
            description="Run what-if scenarios on your lines before you change anything on the floor. Compare throughput, cost, and yield."
          />
          <FeatureCard
            icon={<Camera className="h-4 w-4" />}
            title="AI quality scanner"
            description="Point a camera at your fabric and let YOLO detect defects in real time, right inside your pipeline."
          />
          <FeatureCard
            icon={<BarChart3 className="h-4 w-4" />}
            title="KPI tracking"
            description="Define OEE, throughput, defect rate or any other metric, per line or per machine. Track targets and trends over time."
          />
          <FeatureCard
            icon={<Brain className="h-4 w-4" />}
            title="AI suggestions"
            description="Get actionable recommendations based on real production data. The system learns what works and what doesn't."
          />
          <FeatureCard
            icon={<Shield className="h-4 w-4" />}
            title="Alerts & monitoring"
            description="Critical, high, medium severity. Acknowledge, resolve, track. No alert goes unnoticed on the floor."
          />
        </div>
      </section>

      {/* ── How it works ──────────────────────────────── */}
      <section className="border-t border-neutral-900">
        <div className="max-w-[1200px] mx-auto px-5 py-20">
          <div className="mb-12">
            <p className="text-[11px] font-medium text-neutral-600 uppercase tracking-wider mb-2">
              How it works
            </p>
            <h2 className="text-2xl font-semibold text-white tracking-tight">
              From blueprint to production in three steps
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StepCard
              step="01"
              title="Model your line"
              description="Use the pipeline builder to lay out machines, define process stages, and configure parameters."
            />
            <StepCard
              step="02"
              title="Simulate before acting"
              description="Run simulations with different configurations. Compare output, cost, and quality before touching any machine."
            />
            <StepCard
              step="03"
              title="Monitor everything"
              description="Track KPIs, receive alerts, review AI suggestions, and inspect quality with the integrated scanner."
            />
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────── */}
      <section className="border-t border-neutral-900">
        <div className="max-w-[1200px] mx-auto px-5 py-20 text-center">
          <h2 className="text-2xl md:text-3xl font-semibold text-white tracking-tight mb-4">
            Ready to optimise your production?
          </h2>
          <p className="text-sm text-neutral-500 mb-8 max-w-md mx-auto">
            Create an account and start modelling your first line in minutes.
            No credit card, no setup fee.
          </p>
          <div className="flex items-center justify-center gap-3">
            {isHydrated && isAuthenticated ? (
              <Link
                to="/dashboard"
                className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-black bg-white hover:bg-neutral-200 rounded-[8px] transition-colors"
              >
                Go to Dashboard
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/register"
                  className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-black bg-white hover:bg-neutral-200 rounded-[8px] transition-colors"
                >
                  Create free account
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
                <Link
                  to="/login"
                  className="flex items-center gap-2 px-5 py-2.5 text-sm text-neutral-400 hover:text-white border border-neutral-800 hover:border-neutral-700 rounded-[8px] transition-colors"
                >
                  Sign in
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────── */}
      <footer className="border-t border-neutral-900">
        <div className="max-w-[1200px] mx-auto px-5 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Factory className="h-3.5 w-3.5 text-neutral-600" />
            <span className="text-[12px] text-neutral-600">
              indus.io — Textile production intelligence
            </span>
          </div>
          <div className="flex items-center gap-4 text-[12px] text-neutral-600">
            {isHydrated && isAuthenticated ? (
              <Link to="/dashboard" className="hover:text-neutral-400 transition-colors">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="hover:text-neutral-400 transition-colors">
                  Log in
                </Link>
                <Link to="/register" className="hover:text-neutral-400 transition-colors">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

// ── Sub-components ────────────────────────────────

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="group border border-neutral-800 rounded-lg p-5 hover:border-neutral-700 transition-all bg-neutral-950/50">
      <div className="flex items-center justify-center w-8 h-8 rounded-[7px] bg-neutral-900 border border-neutral-800 text-neutral-300 mb-4 group-hover:border-neutral-700 transition-colors">
        {icon}
      </div>
      <h3 className="text-sm font-medium text-white mb-1.5">{title}</h3>
      <p className="text-xs text-neutral-500 leading-relaxed">{description}</p>
    </div>
  );
}

function StepCard({
  step,
  title,
  description,
}: {
  step: string;
  title: string;
  description: string;
}) {
  return (
    <div className="border border-neutral-800 rounded-lg p-5 bg-neutral-950/50">
      <span className="text-[11px] font-mono text-neutral-600 uppercase tracking-wider">
        Step {step}
      </span>
      <h3 className="text-sm font-medium text-white mt-3 mb-2">{title}</h3>
      <p className="text-xs text-neutral-500 leading-relaxed">{description}</p>
    </div>
  );
}
