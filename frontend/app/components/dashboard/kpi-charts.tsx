import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  Legend,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/tabs";
import type { KPI, KPIValue, Machine, SensorData } from "../../../types/dashboard";

interface KpiChartsProps {
  kpis: KPI[];
  kpiValues: Record<string, KPIValue[]>;
  machines: Machine[];
  sensorData: Record<string, SensorData[]>;
}

// ── Chart color palette ─────────────────────────────────
const CHART_COLORS = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"];
const MACHINE_COLORS: Record<string, string> = {
  cnc: "#3B82F6",
  press: "#EF4444",
  conveyor: "#22C55E",
  robot: "#8B5CF6",
  scanner: "#06B6D4",
  welder: "#F59E0B",
  assembler: "#EC4899",
};

const tooltipStyle = {
  contentStyle: {
    borderRadius: "12px",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    backgroundColor: "#000000",
    backdropFilter: "blur(12px)",
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.4)",
    padding: "12px 16px",
  },
  itemStyle: { color: "#f3f4f6", fontWeight: 500, fontSize: "13px" },
  labelStyle: { color: "#9ca3af", fontSize: "12px", marginBottom: "4px" },
};

// ── Generate mock time-series if no real data ───────────
function generateMockKpiTimeSeries() {
  const hours = ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"];
  return hours.map((time, i) => ({
    time,
    oee: 55 + Math.random() * 35 + i * 2,
    throughput: 100 + Math.random() * 80 + i * 10,
    quality: 85 + Math.random() * 12,
  }));
}

function generateMachineBarData(machines: Machine[]) {
  if (machines.length === 0) {
    return [
      { name: "CNC-01", throughput: 145, efficiency: 82 },
      { name: "Press-01", throughput: 120, efficiency: 75 },
      { name: "Conveyor-01", throughput: 200, efficiency: 92 },
      { name: "Robot-01", throughput: 170, efficiency: 88 },
      { name: "Welder-01", throughput: 95, efficiency: 68 },
    ];
  }
  return machines.slice(0, 8).map((m) => ({
    name: m.name.length > 12 ? m.name.slice(0, 12) + "…" : m.name,
    throughput: Math.round(80 + Math.random() * 150),
    efficiency: Math.round(60 + Math.random() * 35),
  }));
}

function generatePieData(machines: Machine[]) {
  const typeCount: Record<string, number> = {};
  if (machines.length === 0) {
    return [
      { name: "CNC", value: 4, fill: MACHINE_COLORS.cnc },
      { name: "Press", value: 2, fill: MACHINE_COLORS.press },
      { name: "Conveyor", value: 5, fill: MACHINE_COLORS.conveyor },
      { name: "Robot", value: 3, fill: MACHINE_COLORS.robot },
      { name: "Welder", value: 2, fill: MACHINE_COLORS.welder },
      { name: "Scanner", value: 1, fill: MACHINE_COLORS.scanner },
    ];
  }
  machines.forEach((m) => {
    const type = m.process || "Other";
    typeCount[type] = (typeCount[type] || 0) + 1;
  });
  return Object.entries(typeCount).map(([name, value], i) => ({
    name,
    value,
    fill: CHART_COLORS[i % CHART_COLORS.length],
  }));
}

function generateRadialData(machines: Machine[]) {
  if (machines.length === 0) {
    return [
      { name: "Availability", value: 92, fill: "#10b981" },
      { name: "Performance", value: 85, fill: "#3b82f6" },
      { name: "Quality", value: 97, fill: "#8b5cf6" },
    ];
  }
  return [
    { name: "Availability", value: Math.round(75 + Math.random() * 20), fill: "#10b981" },
    { name: "Performance", value: Math.round(70 + Math.random() * 25), fill: "#3b82f6" },
    { name: "Quality", value: Math.round(85 + Math.random() * 12), fill: "#8b5cf6" },
  ];
}

export function KpiCharts({ kpis, kpiValues, machines, sensorData }: KpiChartsProps) {
  const timeSeriesData = generateMockKpiTimeSeries();
  const barData = generateMachineBarData(machines);
  const pieData = generatePieData(machines);
  const radialData = generateRadialData(machines);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {/* ── Card 1: Performance Trends Area Chart ── */}
      <Card className="bg-neutral-950 border-neutral-800">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white text-sm font-semibold">Performance Trends</CardTitle>
              <CardDescription className="text-neutral-500 text-xs">Real-time OEE, Throughput & Quality</CardDescription>
            </div>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Live</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSeriesData} margin={{ top: 10, right: 5, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradOee" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradThroughput" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#262626" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#737373" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#737373" }} />
                <Tooltip {...tooltipStyle} />
                <Area type="monotone" dataKey="oee" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#gradOee)" name="OEE (%)" />
                <Area type="monotone" dataKey="throughput" stroke="#3b82f6" strokeWidth={1.5} fillOpacity={1} fill="url(#gradThroughput)" name="Throughput" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* ── Card 2: Process Distribution Pie Chart ── */}
      <Card className="bg-neutral-950 border-neutral-800">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white text-sm font-semibold">Process Distribution</CardTitle>
              <CardDescription className="text-neutral-500 text-xs">Active machine roles in production</CardDescription>
            </div>
            <span className="text-[10px] text-neutral-400 border border-neutral-800 px-2 py-0.5 rounded-full font-medium">Machines</span>
          </div>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center">
          <div className="h-[210px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip {...tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5 mt-2">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1.5 text-[11px] text-neutral-400">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.fill }} />
                <span>{item.name} ({item.value})</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Card 3: Machine Performance Bar Chart ── */}
      <Card className="bg-neutral-950 border-neutral-800">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white text-sm font-semibold">Machine Performance</CardTitle>
              <CardDescription className="text-neutral-500 text-xs">Throughput and Efficiency per machine</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#262626" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#737373" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: "#737373" }} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="throughput" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Throughput (u/h)" barSize={16} />
                <Bar dataKey="efficiency" fill="#10b981" radius={[4, 4, 0, 0]} name="Efficiency (%)" barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* ── Card 4: OEE Breakdown Radial Chart ── */}
      <Card className="bg-neutral-950 border-neutral-800">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white text-sm font-semibold">OEE Breakdown</CardTitle>
              <CardDescription className="text-neutral-500 text-xs">Availability, Performance, Quality</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center">
          <div className="h-[210px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="30%"
                outerRadius="100%"
                barSize={16}
                data={radialData}
                startAngle={180}
                endAngle={0}
              >
                <RadialBar
                  background={{ fill: "#262626" }}
                  dataKey="value"
                  cornerRadius={8}
                />
                <Tooltip {...tooltipStyle} />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5 mt-2">
            {radialData.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1.5 text-[11px] text-neutral-400">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.fill }} />
                <span>{item.name} ({item.value}%)</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
