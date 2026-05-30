import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Clock,
  Factory,
  Gauge,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { kpiService, lineService, machineService } from "../../lib/api";
import type { KPI, KPIValue, Machine, ProductionLine } from "../../types/dashboard";
import { Protect } from "~/features/auth/components/protect";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

type RangeKey = "24h" | "7d" | "30d" | "all";

const ranges: { key: RangeKey; label: string; hours?: number }[] = [
  { key: "24h", label: "24H", hours: 24 },
  { key: "7d", label: "7D", hours: 24 * 7 },
  { key: "30d", label: "30D", hours: 24 * 30 },
  { key: "all", label: "All" },
];

const lowerIsBetterTerms = ["defect", "scrap", "waste", "reject", "downtime", "error", "loss"];

function lowerIsBetter(kpi?: KPI | null) {
  if (!kpi) return false;
  const text = `${kpi.name} ${kpi.formula ?? ""}`.toLowerCase();
  return lowerIsBetterTerms.some((term) => text.includes(term));
}

function formatNumber(value?: number | null, digits = 2) {
  if (value == null || Number.isNaN(value)) return "N/A";
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: Math.abs(value) < 10 ? Math.min(digits, 2) : 0,
  }).format(value);
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function getStatus(kpi: KPI, current?: number | null) {
  if (current == null || kpi.target_value == null) {
    return { label: "No target", tone: "text-neutral-400", bg: "bg-neutral-500/10", border: "border-neutral-800" };
  }

  const passed = lowerIsBetter(kpi) ? current <= kpi.target_value : current >= kpi.target_value;
  return passed
    ? { label: "On target", tone: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" }
    : { label: "Needs attention", tone: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" };
}

export default function KpiDetails() {
  const { kpiId } = useParams();
  const navigate = useNavigate();
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [values, setValues] = useState<KPIValue[]>([]);
  const [line, setLine] = useState<ProductionLine | null>(null);
  const [machine, setMachine] = useState<Machine | null>(null);
  const [range, setRange] = useState<RangeKey>("7d");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadKpi() {
      if (!kpiId) return;
      setIsLoading(true);
      setError(null);

      try {
        const [kpiRes, valuesRes] = await Promise.all([
          kpiService.get(kpiId),
          kpiService.getValues(kpiId),
        ]);

        if (cancelled) return;

        const nextKpi = kpiRes.data;
        const sortedValues = [...valuesRes.data].sort(
          (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );

        setKpi(nextKpi);
        setValues(sortedValues);

        const [lineRes, machineRes] = await Promise.all([
          lineService.get(nextKpi.production_line_id).catch(() => null),
          nextKpi.machine_id ? machineService.get(nextKpi.machine_id).catch(() => null) : Promise.resolve(null),
        ]);

        if (!cancelled) {
          setLine(lineRes?.data ?? null);
          setMachine(machineRes?.data ?? null);
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.response?.status === 404 ? "KPI not found" : "Unable to load KPI data");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    loadKpi();
    return () => {
      cancelled = true;
    };
  }, [kpiId]);

  const filteredValues = useMemo(() => {
    const selected = ranges.find((item) => item.key === range);
    if (!selected?.hours) return values;

    const cutoff = Date.now() - selected.hours * 60 * 60 * 1000;
    return values.filter((item) => new Date(item.timestamp).getTime() >= cutoff);
  }, [range, values]);

  const stats = useMemo(() => {
    const current = filteredValues.at(-1)?.value ?? null;
    const previous = filteredValues.length > 1 ? filteredValues.at(-2)?.value ?? null : null;
    const all = filteredValues.map((item) => item.value);
    const average = all.length ? all.reduce((sum, value) => sum + value, 0) / all.length : null;
    const min = all.length ? Math.min(...all) : null;
    const max = all.length ? Math.max(...all) : null;
    const delta = current != null && previous != null ? current - previous : null;
    const targetDelta = current != null && kpi?.target_value != null ? current - kpi.target_value : null;

    return { current, previous, average, min, max, delta, targetDelta };
  }, [filteredValues, kpi?.target_value]);

  const status = kpi ? getStatus(kpi, stats.current) : null;
  const chartData = filteredValues.map((item) => ({
    timestamp: item.timestamp,
    time: formatDateTime(item.timestamp),
    value: item.value,
    target: kpi?.target_value ?? undefined,
  }));
  const trendUp = (stats.delta ?? 0) >= 0;
  const trendIsGood = kpi ? (lowerIsBetter(kpi) ? !trendUp : trendUp) : true;
  const lineColor = status?.label === "Needs attention" ? "#f59e0b" : "#10b981";

  if (isLoading) {
    return (
      <Protect>
        <div className="min-h-screen bg-black text-neutral-400 flex items-center justify-center">
          <div className="flex items-center gap-3 text-sm">
            <Activity className="h-4 w-4 animate-pulse text-emerald-400" />
            Loading KPI history
          </div>
        </div>
      </Protect>
    );
  }

  if (error || !kpi) {
    return (
      <Protect>
        <div className="min-h-screen bg-black text-neutral-200 flex items-center justify-center px-5">
          <div className="max-w-sm text-center">
            <AlertTriangle className="mx-auto h-9 w-9 text-amber-400 mb-4" />
            <h1 className="text-xl font-semibold text-white">{error ?? "KPI not found"}</h1>
            <p className="text-sm text-neutral-500 mt-2">The KPI may have been removed or your session no longer has access.</p>
            <Button className="mt-5" variant="outline" onClick={() => navigate("/")}>
              <ArrowLeft className="h-4 w-4" />
              Dashboard
            </Button>
          </div>
        </div>
      </Protect>
    );
  }

  return (
    <Protect>
      <div className="min-h-screen bg-black text-neutral-200 font-sans">
        <header className="sticky top-0 z-50 border-b border-neutral-800 bg-black/80 backdrop-blur-md">
          <div className="max-w-[1440px] mx-auto h-12 px-5 flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-white">
                <Factory className="h-4 w-4" />
                indus.io
              </Link>
              <span className="text-neutral-700">/</span>
              <span className="text-sm text-neutral-400 truncate">KPI Details</span>
            </div>
            <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-3.5 w-3.5" />
              Back
            </Button>
          </div>
        </header>

        <main className="max-w-[1440px] mx-auto px-5 py-6 space-y-6">
          <section className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                {status && (
                  <span className={`inline-flex items-center rounded-md border px-2 py-1 text-[11px] font-medium ${status.bg} ${status.border} ${status.tone}`}>
                    {status.label}
                  </span>
                )}
                <span className="text-xs text-neutral-500">{line?.name ?? "Production line"}</span>
                {machine && (
                  <>
                    <span className="text-neutral-700">/</span>
                    <span className="text-xs text-neutral-500">{machine.name}</span>
                  </>
                )}
              </div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">{kpi.name}</h1>
              <p className="text-sm text-neutral-500 mt-2 max-w-2xl">
                {kpi.formula ? `Formula: ${kpi.formula}` : "Historical KPI tracking with target comparison."}
              </p>
            </div>

            <div className="inline-flex h-9 rounded-lg border border-neutral-800 bg-neutral-950 p-1">
              {ranges.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setRange(item.key)}
                  className={`px-3 text-xs font-medium rounded-md transition-colors cursor-pointer ${
                    range === item.key ? "bg-neutral-800 text-white" : "text-neutral-500 hover:text-neutral-200"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </section>

          <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <MetricCard
              icon={<Gauge className="h-4 w-4" />}
              label="Current"
              value={formatNumber(stats.current)}
              unit={kpi.unit}
              detail={filteredValues.at(-1) ? formatDateTime(filteredValues.at(-1)!.timestamp) : "No samples"}
              tone={status?.tone}
            />
            <MetricCard
              icon={<Target className="h-4 w-4" />}
              label="Target"
              value={formatNumber(kpi.target_value)}
              unit={kpi.unit}
              detail={lowerIsBetter(kpi) ? "Lower is better" : "Higher is better"}
            />
            <MetricCard
              icon={trendUp ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              label="Last Change"
              value={stats.delta == null ? "N/A" : `${stats.delta > 0 ? "+" : ""}${formatNumber(stats.delta)}`}
              unit={kpi.unit}
              detail={stats.previous == null ? "Need two samples" : trendIsGood ? "Moving favorably" : "Moving away"}
              tone={stats.delta == null ? "text-neutral-400" : trendIsGood ? "text-emerald-400" : "text-amber-400"}
            />
            <MetricCard
              icon={<BarChart3 className="h-4 w-4" />}
              label="Average"
              value={formatNumber(stats.average)}
              unit={kpi.unit}
              detail={`${filteredValues.length} sample${filteredValues.length === 1 ? "" : "s"} in range`}
            />
          </section>

          <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_360px] gap-5">
            <Card className="bg-neutral-950 border-neutral-800 rounded-lg">
              <CardHeader className="pb-0">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <CardTitle className="text-sm font-semibold text-white">Historical Values</CardTitle>
                    <p className="text-xs text-neutral-500 mt-1">Actual values plotted against the KPI target.</p>
                  </div>
                  {kpi.target_value != null && (
                    <div className="hidden sm:flex items-center gap-2 text-xs text-neutral-500">
                      <span className="h-px w-8 border-t border-dashed border-red-400" />
                      Target {formatNumber(kpi.target_value)} {kpi.unit}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-[420px] w-full">
                  {chartData.length === 0 ? (
                    <div className="h-full flex items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-500">
                      No KPI values found for this range
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData} margin={{ top: 24, right: 20, left: -10, bottom: 8 }}>
                        <defs>
                          <linearGradient id="kpiValueGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor={lineColor} stopOpacity={0.32} />
                            <stop offset="95%" stopColor={lineColor} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
                        <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#737373" }} minTickGap={24} />
                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 11, fill: "#737373" }}
                          domain={["auto", "auto"]}
                          tickFormatter={(value) => formatNumber(Number(value), 1)}
                        />
                        <Tooltip
                          contentStyle={{
                            background: "#050505",
                            border: "1px solid #262626",
                            borderRadius: 8,
                            color: "#f5f5f5",
                          }}
                          labelFormatter={(_, payload) => {
                            const row = payload?.[0]?.payload as { timestamp?: string } | undefined;
                            return row?.timestamp ? new Date(row.timestamp).toLocaleString() : "";
                          }}
                          formatter={(value) => [`${formatNumber(Number(value))} ${kpi.unit ?? ""}`, kpi.name]}
                        />
                        {kpi.target_value != null && (
                          <ReferenceLine
                            y={kpi.target_value}
                            stroke="#f87171"
                            strokeDasharray="4 4"
                            label={{ value: "Target", position: "insideTopRight", fill: "#f87171", fontSize: 12 }}
                          />
                        )}
                        <Area
                          type="monotone"
                          dataKey="value"
                          stroke={lineColor}
                          strokeWidth={2}
                          fill="url(#kpiValueGradient)"
                          activeDot={{ r: 5, stroke: "#050505", strokeWidth: 2 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="space-y-5">
              <Card className="bg-neutral-950 border-neutral-800 rounded-lg">
                <CardHeader className="pb-0">
                  <CardTitle className="text-sm font-semibold text-white">Range Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <SummaryRow label="Minimum" value={`${formatNumber(stats.min)} ${kpi.unit ?? ""}`} />
                  <SummaryRow label="Maximum" value={`${formatNumber(stats.max)} ${kpi.unit ?? ""}`} />
                  <SummaryRow
                    label="Target Gap"
                    value={stats.targetDelta == null ? "N/A" : `${stats.targetDelta > 0 ? "+" : ""}${formatNumber(stats.targetDelta)} ${kpi.unit ?? ""}`}
                  />
                  <SummaryRow label="Created" value={formatDateTime(kpi.created_at)} />
                  <SummaryRow label="Updated" value={formatDateTime(kpi.updated_at)} />
                </CardContent>
              </Card>

              <Card className="bg-neutral-950 border-neutral-800 rounded-lg">
                <CardHeader className="pb-0">
                  <CardTitle className="text-sm font-semibold text-white">Recent Samples</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {[...filteredValues].slice(-6).reverse().map((item) => (
                      <div key={item.id} className="flex items-center justify-between rounded-lg border border-neutral-800 bg-black/30 px-3 py-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <Clock className="h-3.5 w-3.5 text-neutral-600 shrink-0" />
                          <span className="text-xs text-neutral-400 truncate">{formatDateTime(item.timestamp)}</span>
                        </div>
                        <span className="text-xs font-medium text-white tabular-nums">
                          {formatNumber(item.value)} {kpi.unit}
                        </span>
                      </div>
                    ))}
                    {filteredValues.length === 0 && (
                      <div className="py-8 text-center text-xs text-neutral-500 border border-dashed border-neutral-800 rounded-lg">
                        No samples in this range
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </section>
        </main>
      </div>
    </Protect>
  );
}

function MetricCard({
  icon,
  label,
  value,
  unit,
  detail,
  tone = "text-white",
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  unit?: string | null;
  detail: string;
  tone?: string;
}) {
  return (
    <Card className="bg-neutral-950 border-neutral-800 rounded-lg">
      <CardContent className="pt-1">
        <div className="flex items-center gap-2 text-xs text-neutral-500 mb-3">
          {icon}
          <span className="uppercase tracking-wider">{label}</span>
        </div>
        <div className={`text-3xl font-semibold tabular-nums ${tone}`}>
          {value}
          {value !== "N/A" && unit && <span className="ml-1 text-sm font-medium text-neutral-500">{unit}</span>}
        </div>
        <p className="text-xs text-neutral-500 mt-2 truncate">{detail}</p>
      </CardContent>
    </Card>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-neutral-900 pb-3 last:border-b-0 last:pb-0">
      <span className="text-xs text-neutral-500">{label}</span>
      <span className="text-xs font-medium text-neutral-200 text-right">{value}</span>
    </div>
  );
}
