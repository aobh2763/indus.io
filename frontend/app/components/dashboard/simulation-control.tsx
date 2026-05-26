import { useState, useEffect } from "react";
import { Play, Square, Check, Activity, Clock, Terminal } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { ScrollArea } from "../ui/scroll-area";
import { Separator } from "../ui/separator";
import type { Simulation, SimulationLog } from "../../../types/dashboard";

interface SimulationControlProps {
  simulation?: Simulation;
  logs?: SimulationLog[];
  onStart?: () => void;
  onStop?: () => void;
  onComplete?: () => void;
}

const statusConfig = {
  RUNNING: { label: "Running", variant: "default" as const, color: "text-emerald-400" },
  STOPPED: { label: "Stopped", variant: "destructive" as const, color: "text-rose-400" },
  COMPLETED: { label: "Completed", variant: "secondary" as const, color: "text-blue-400" },
  NONE: { label: "No Active Simulation", variant: "outline" as const, color: "text-gray-400" },
};

function formatTime(dateStr?: string) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function SimulationControl({ simulation, logs = [], onStart, onStop, onComplete }: SimulationControlProps) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let interval: number;
    if (simulation?.status === "RUNNING" && simulation.start_time) {
      const start = new Date(simulation.start_time).getTime();
      interval = window.setInterval(() => {
        setElapsed(Math.floor((Date.now() - start) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [simulation]);

  const status = simulation?.status || "NONE";
  const config = statusConfig[status];

  const formatDuration = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-emerald-500/10">
              <Activity className="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <CardTitle className="text-base">Simulation Engine</CardTitle>
              <CardDescription>Digital twin execution</CardDescription>
            </div>
          </div>
          <Badge variant={config.variant} className={status === "RUNNING" ? "animate-pulse" : ""}>
            {config.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col pt-0 px-6 pb-6 gap-4">
        <div className="grid grid-cols-2 gap-3 bg-gray-950/50 rounded-lg p-3 border border-gray-800/60">
          <div className="space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">Started At</p>
            <p className="text-sm font-mono text-gray-200">{formatTime(simulation?.start_time)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">Duration</p>
            <p className="text-sm font-mono text-gray-200">
              {simulation?.status === "RUNNING" ? formatDuration(elapsed) : "—"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            className="flex-1"
            variant="default"
            disabled={status === "RUNNING" || status === "COMPLETED"}
            onClick={onStart}
          >
            <Play className="h-4 w-4" /> Start
          </Button>
          <Button
            className="flex-1"
            variant="destructive"
            disabled={status !== "RUNNING"}
            onClick={onStop}
          >
            <Square className="h-4 w-4" /> Stop
          </Button>
          <Button
            className="flex-1"
            variant="secondary"
            disabled={status !== "RUNNING" && status !== "STOPPED"}
            onClick={onComplete}
          >
            <Check className="h-4 w-4" /> Complete
          </Button>
        </div>

        <Separator />

        <div className="flex-1 flex flex-col min-h-[150px]">
          <div className="flex items-center gap-1.5 mb-2">
            <Terminal className="h-3 w-3 text-gray-400" />
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Event Log</span>
          </div>
          <div className="flex-1 bg-gray-950 rounded-lg border border-gray-800 p-2 font-mono text-[10px] sm:text-xs">
            <ScrollArea maxHeight="120px" className="h-full">
              {logs.length > 0 ? (
                <div className="space-y-1">
                  {logs.map((log) => (
                    <div key={log.id} className="flex gap-2 text-gray-300">
                      <span className="text-gray-500 shrink-0">[{formatTime(log.created_at)}]</span>
                      <span className={
                        log.level === "ERROR" ? "text-rose-400" :
                          log.level === "WARNING" ? "text-amber-400" : "text-blue-400"
                      }>
                        [{log.level}]
                      </span>
                      <span className="break-all">{log.message}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-gray-600">
                  Waiting for simulation events...
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
