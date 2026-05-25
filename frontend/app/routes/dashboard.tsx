import { Link } from "react-router";
import {
  Activity,
  AlertCircle,
  Briefcase,
  CheckCircle2,
  TrendingUp,
  Clock,
  Factory,
  ArrowRight,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import {
  ReactFlow,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { Protect } from "~/features/auth/components/protect";
import { Navbar1 } from "~/components/navbar";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";

import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Progress } from "~/components/ui/progress";
import { Separator } from "~/components/ui/separator";

const kpiData = [
  { time: "08:00", oee: 65, throughput: 120 },
  { time: "10:00", oee: 72, throughput: 145 },
  { time: "12:00", oee: 68, throughput: 130 },
  { time: "14:00", oee: 78, throughput: 160 },
  { time: "16:00", oee: 82, throughput: 175 },
  { time: "18:00", oee: 85, throughput: 190 },
];

const mockNodes = [
  {
    id: "1",
    position: { x: 50, y: 50 },
    data: { label: "Matière Première" },
    style: {
      width: 130,
      fontSize: "12px",
      padding: "8px",
      borderRadius: "12px",
      border: "1px solid hsl(var(--border))",
      background: "hsl(var(--card))",
      color: "hsl(var(--foreground))",
    },
  },
  {
    id: "2",
    position: { x: 240, y: 50 },
    data: { label: "Coupe" },
    style: {
      width: 100,
      fontSize: "12px",
      padding: "8px",
      borderRadius: "12px",
      border: "1px solid hsl(var(--border))",
      background: "hsl(var(--card))",
      color: "hsl(var(--foreground))",
    },
  },
  {
    id: "3",
    position: { x: 410, y: 50 },
    data: { label: "Assemblage" },
    style: {
      width: 120,
      fontSize: "12px",
      padding: "8px",
      borderRadius: "12px",
      border: "1px solid hsl(var(--border))",
      background: "hsl(var(--card))",
      color: "hsl(var(--foreground))",
    },
  },
];

const mockEdges = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
];

export default function HomePage() {
  return (
    <Protect>
      <div className="min-h-screen bg-background">
        <Navbar1 />

        <main className="mx-auto space-y-6 px-6 pb-8 pt-24">
          {/* Header */}
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                Dashboard Industriel
              </h1>

              <p className="text-muted-foreground">
                Monitoring en temps réel de la production et des pipelines.
              </p>
            </div>

            <Button asChild>
              <Link to="/pipeline-builder">
                Ouvrir Pipeline Builder
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          {/* KPI GRID */}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              title="OEE Moyen"
              value="78.5%"
              description="+2.5% depuis hier"
              icon={Activity}
              trend="positive"
            />

            <KpiCard
              title="Rendement"
              value="1,240"
              description="+15% par rapport à l'objectif"
              icon={TrendingUp}
              trend="positive"
            />

            <KpiCard
              title="Projets en cours"
              value="12"
              description="3 en retard"
              icon={Briefcase}
              trend="neutral"
            />

            <KpiCard
              title="Alertes Machines"
              value="4"
              description="Attention immédiate requise"
              icon={AlertCircle}
              trend="negative"
            />
          </div>

          {/* CONTENT GRID */}
          <div className="grid gap-6 lg:grid-cols-7">
            {/* LEFT */}
            <div className="space-y-6 lg:col-span-4">
              {/* CHART */}
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>
                    Performance Globale
                  </CardTitle>

                  <CardDescription>
                    Évolution de la production et de l'OEE.
                  </CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="h-[320px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={kpiData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: -20,
                          bottom: 0,
                        }}
                      >
                        <defs>
                          <linearGradient
                            id="colorOee"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="5%"
                              stopColor="hsl(var(--primary))"
                              stopOpacity={0.3}
                            />
                            <stop
                              offset="95%"
                              stopColor="hsl(var(--primary))"
                              stopOpacity={0}
                            />
                          </linearGradient>
                        </defs>

                        <CartesianGrid
                          strokeDasharray="3 3"
                          vertical={false}
                          className="stroke-muted"
                        />

                        <XAxis
                          dataKey="time"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 12 }}
                        />

                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 12 }}
                        />

                        <Tooltip
                          contentStyle={{
                            borderRadius: "12px",
                            border: "1px solid hsl(var(--border))",
                            background: "hsl(var(--background))",
                          }}
                        />

                        <Area
                          type="monotone"
                          dataKey="oee"
                          stroke="hsl(var(--primary))"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#colorOee)"
                          name="OEE (%)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* PROJECTS */}
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle>
                    Projets Récents
                  </CardTitle>

                  <CardDescription>
                    Suivi des commandes et de leur progression.
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-5">
                  <ProjectItem
                    name="Lot T-Shirts Hiver"
                    progress={85}
                    expected="Aujourd'hui"
                    status="Bon"
                  />

                  <Separator />

                  <ProjectItem
                    name="Pantalons Denim Q3"
                    progress={45}
                    expected="Dans 3 jours"
                    status="Retard"
                  />

                  <Separator />

                  <ProjectItem
                    name="Vestes Légères"
                    progress={15}
                    expected="Semaine prochaine"
                    status="Bon"
                  />
                </CardContent>
              </Card>
            </div>

            {/* RIGHT */}
            <div className="space-y-6 lg:col-span-3">
              {/* PIPELINE */}
              <Card className="border-border/60">
                <CardHeader className="flex flex-row items-start justify-between space-y-0">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Factory className="h-5 w-5" />
                      Pipeline de Production
                    </CardTitle>

                    <CardDescription>
                      Aperçu rapide du workflow industriel.
                    </CardDescription>
                  </div>

                  <Button
                    asChild
                    variant="secondary"
                    size="sm"
                  >
                    <Link to="/pipeline-builder">
                      Détails
                    </Link>
                  </Button>
                </CardHeader>

                <CardContent>
                  <div className="relative h-[300px] overflow-hidden rounded-xl border bg-muted/20">
                    <ReactFlow
                      nodes={mockNodes}
                      edges={mockEdges}
                      fitView
                      proOptions={{ hideAttribution: true }}
                      panOnScroll={false}
                      zoomOnScroll={false}
                      zoomOnPinch={false}
                      zoomOnDoubleClick={false}
                      nodesDraggable={false}
                      nodesConnectable={false}
                      elementsSelectable={false}
                    >
                      <Background gap={16} />
                    </ReactFlow>

                    <Link
                      to="/pipeline-builder"
                      className="absolute inset-0 z-10"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* ALERTS */}
              <Card className="border-border/60">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-destructive" />
                    Alertes IA & Machines
                  </CardTitle>

                  <CardDescription>
                    Événements critiques détectés par le système.
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <AlertItem
                    type="critical"
                    time="Il y a 10 min"
                    message="Machine Coupe-02: baisse de performance détectée."
                  />

                  <AlertItem
                    type="warning"
                    time="Il y a 1 heure"
                    message="Goulot d'étranglement prédit sur l'atelier couture."
                  />

                  <AlertItem
                    type="info"
                    time="Il y a 3 heures"
                    message="Maintenance préventive recommandée."
                  />
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </Protect>
  );
}

type KpiCardProps = {
  title: string;
  value: string;
  description: string;
  icon: any;
  trend: "positive" | "negative" | "neutral";
};

function KpiCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
}: KpiCardProps) {
  return (
    <Card className="border-border/60">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              {title}
            </p>

            <h3 className="text-3xl font-bold tracking-tight">
              {value}
            </h3>

            <Badge
              variant={
                trend === "positive"
                  ? "default"
                  : trend === "negative"
                    ? "destructive"
                    : "secondary"
              }
            >
              {description}
            </Badge>
          </div>

          <div className="rounded-xl border bg-muted p-3">
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

type ProjectItemProps = {
  name: string;
  progress: number;
  expected: string;
  status: string;
};

function ProjectItem({
  name,
  progress,
  expected,
  status,
}: ProjectItemProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h4 className="font-medium">
            {name}
          </h4>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            {expected}
          </div>
        </div>

        <Badge
          variant={
            status === "Retard"
              ? "destructive"
              : "secondary"
          }
        >
          {status}
        </Badge>
      </div>

      <div className="flex items-center gap-3">
        <Progress value={progress} className="h-2" />

        <span className="w-10 text-right text-sm font-medium">
          {progress}%
        </span>
      </div>
    </div>
  );
}

type AlertItemProps = {
  type: "critical" | "warning" | "info";
  message: string;
  time: string;
};

function AlertItem({
  type,
  message,
  time,
}: AlertItemProps) {
  const styles = {
    critical: {
      wrapper:
        "border-destructive/30 bg-destructive/10",
      text: "text-destructive",
      icon: AlertCircle,
    },

    warning: {
      wrapper:
        "border-yellow-500/30 bg-yellow-500/10",
      text: "text-yellow-500",
      icon: Activity,
    },

    info: {
      wrapper:
        "border-blue-500/30 bg-blue-500/10",
      text: "text-blue-500",
      icon: CheckCircle2,
    },
  };

  const config = styles[type];
  const Icon = config.icon;

  return (
    <div
      className={`rounded-xl border p-4 ${config.wrapper}`}
    >
      <div className="flex items-start gap-3">
        <div className={config.text}>
          <Icon className="mt-0.5 h-5 w-5" />
        </div>

        <div className="space-y-1">
          <p className="text-sm font-medium leading-relaxed">
            {message}
          </p>

          <p className="text-xs text-muted-foreground">
            {time}
          </p>
        </div>
      </div>
    </div>
  );
}
