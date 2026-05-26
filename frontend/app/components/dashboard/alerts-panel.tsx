import { AlertCircle, AlertTriangle, Info, Bell, Shield } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { ScrollArea } from "../ui/scroll-area";
import { Separator } from "../ui/separator";
import { cn } from "../../../lib/utils";
import type { Alert } from "../../../types/dashboard";

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge?: (id: string) => void;
  onResolve?: (id: string) => void;
}

const severityConfig: Record<string, any> = {
  CRITICAL: { icon: AlertCircle, bg: "bg-red-500/8", border: "border-red-500/20", iconColor: "text-red-400", pulse: true, badgeVariant: "destructive" },
  HIGH: { icon: AlertTriangle, bg: "bg-orange-500/8", border: "border-orange-500/20", iconColor: "text-orange-400", pulse: false, badgeVariant: "warning" },
  MEDIUM: { icon: Bell, bg: "bg-amber-500/8", border: "border-amber-500/20", iconColor: "text-amber-400", pulse: false, badgeVariant: "warning" },
  LOW: { icon: Info, bg: "bg-blue-500/8", border: "border-blue-500/20", iconColor: "text-blue-400", pulse: false, badgeVariant: "default" },
};

const statusVariant: Record<string, any> = {
  OPEN: { label: "Open", variant: "destructive" },
  IN_PROGRESS: { label: "In Progress", variant: "warning" },
  RESOLVED: { label: "Resolved", variant: "success" },
};

function timeAgo(d: string) {
  const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

const mockAlerts: Alert[] = [
  { id: "m1", production_line_id: "", type: "machine_failure", severity: "CRITICAL", message: "CNC-02: Performance below threshold (OEE < 50%)", status: "OPEN", acknowledged: false, created_at: new Date(Date.now() - 600000).toISOString() },
  { id: "m2", production_line_id: "", type: "bottleneck", severity: "HIGH", message: "Bottleneck predicted on Assembly line within 2h", status: "OPEN", acknowledged: false, created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: "m3", production_line_id: "", type: "maintenance", severity: "MEDIUM", message: "Preventive maintenance recommended for Welder-01", status: "IN_PROGRESS", acknowledged: true, created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: "m4", production_line_id: "", type: "quality", severity: "LOW", message: "Quality score dipped 2% on Conveyor Belt 3", status: "RESOLVED", acknowledged: true, created_at: new Date(Date.now() - 86400000).toISOString(), resolved_at: new Date().toISOString() },
];

export function AlertsPanel({ alerts, onAcknowledge, onResolve }: AlertsPanelProps) {
  const data = alerts.length > 0 ? alerts : mockAlerts;
  const openCount = data.filter((a) => a.status === "OPEN").length;

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-rose-500/10">
              <Shield className="h-4 w-4 text-rose-400" />
            </div>
            <div>
              <CardTitle className="text-base">Alerts & Monitoring</CardTitle>
              <CardDescription>System notifications</CardDescription>
            </div>
          </div>
          {openCount > 0 && <Badge variant="destructive" className="animate-pulse">{openCount} open</Badge>}
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="flex-1 pt-4">
        <ScrollArea maxHeight="400px" className="pr-1">
          <div className="space-y-3">
            {data.map((alert) => {
              const cfg = severityConfig[alert.severity] || severityConfig.LOW;
              const st = statusVariant[alert.status] || statusVariant.OPEN;
              const Icon = cfg.icon;
              return (
                <div key={alert.id} className={cn("flex items-start gap-3 p-3.5 rounded-lg border transition-all duration-200", cfg.bg, cfg.border, alert.status === "RESOLVED" && "opacity-50")}>
                  <div className={cn("mt-0.5 shrink-0", cfg.iconColor, cfg.pulse && "animate-pulse")}><Icon className="h-4 w-4" /></div>
                  <div className="flex-1 min-w-0 space-y-2">
                    <p className="text-sm font-medium text-gray-200 leading-snug">{alert.message}</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant={cfg.badgeVariant} className="text-[10px] px-1.5 py-0">{alert.severity}</Badge>
                      <Badge variant={st.variant} className="text-[10px] px-1.5 py-0">{st.label}</Badge>
                      <span className="text-[11px] text-gray-500">{timeAgo(alert.created_at)}</span>
                    </div>
                    {alert.status !== "RESOLVED" && (
                      <div className="flex items-center gap-1.5 pt-1">
                        {!alert.acknowledged && onAcknowledge && <Button variant="ghost" size="sm" className="h-6 text-[11px] px-2 text-amber-400 hover:text-amber-300" onClick={() => onAcknowledge(alert.id)}>Acknowledge</Button>}
                        {alert.acknowledged && onResolve && <Button variant="ghost" size="sm" className="h-6 text-[11px] px-2 text-emerald-400 hover:text-emerald-300" onClick={() => onResolve(alert.id)}>Resolve</Button>}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
