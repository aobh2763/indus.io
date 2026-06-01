import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { STEP, type SimulationFrame, type SimulationLink, type SimulationResponse, SimulationStatus } from "../simulations.schema";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "~/components/ui/accordion";

import { cn } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import { useSimulationStore } from "../simulations.store";
import { AlertTriangle, CheckCircle2, XCircle, ChevronRight, Activity, Layers, Zap, ArrowLeft, Wand2 } from "lucide-react";
import { useGetSimulationSteps, useUpdateSimulation } from "../simulations.hooks";
import { Textarea } from "~/components/ui/textarea";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export interface SimulationInspectProps {
  data: SimulationResponse;
}

function statusBadge(status: SimulationStatus) {
  const map = {
    [SimulationStatus.RUNNING]: { label: "Running", class: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
    [SimulationStatus.COMPLETED]: { label: "Completed", class: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
    [SimulationStatus.STOPPED]: { label: "Stopped", class: "bg-muted/50 text-muted-foreground border-border" },
  };
  const cfg = map[status];
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold tracking-wide uppercase", cfg.class)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", {
        "bg-blue-400 animate-pulse": status === SimulationStatus.RUNNING,
        "bg-emerald-400": status === SimulationStatus.COMPLETED,
        "bg-muted-foreground": status === SimulationStatus.STOPPED,
      })} />
      {cfg.label}
    </span>
  );
}

function formatKey(key: string) {
  return key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
  return String(value);
}

function isWarningLevel(key: string, value: unknown) {
  if (typeof value === "string" && (value.toLowerCase().includes("high") || value.toLowerCase().includes("medium"))) return "warn";
  if (typeof value === "string" && value.toLowerCase().includes("low")) return "ok";
  if (key.includes("risk") || key.includes("warning")) return "warn";
  return null;
}

function AttributeRow({ label, value }: { label: string; value: unknown }) {
  const level = isWarningLevel(label, value);
  return (
    <div className="flex items-start justify-between gap-3 py-1.5 group">
      <span className="text-[11px] text-muted-foreground leading-tight min-w-0 flex-1 truncate group-hover:text-foreground transition-colors">
        {formatKey(label)}
      </span>
      <span className={cn(
        "text-[11px] text-right shrink-0",
        level === "warn" && "text-amber-400",
        level === "ok" && "text-emerald-400",
        !level && "text-foreground",
      )}>
        {formatValue(value)}
      </span>
    </div>
  );
}

function RecordCard({ id, data, label }: { id: string; data: Record<string, unknown>; label?: string }) {
  const shortId = id.slice(-8);
  return (
    <div className="rounded-lg border border-border bg-muted/20 overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 bg-muted/30 border-b border-border">
        <Layers className="h-3 w-3 text-muted-foreground" />
        <span className="text-[11px] text-muted-foreground font-semibold tracking-wider">{label ?? "Record"}</span>
        <span className="ml-auto text-[11px] text-muted-foreground/50">...{shortId}</span>
      </div>
      <div className="px-3 divide-y divide-border/60">
        {Object.entries(data).map(([k, v]) =>
          k !== "warnings" ? <AttributeRow key={k} label={k} value={v} /> : null
        )}
        {typeof data.warnings === "string" && data.warnings && (
          <div className="py-2">
            <WarningBlock text={data.warnings} />
          </div>
        )}
      </div>
    </div>
  );
}

function WarningBlock({ text }: { text: string }) {
  const warnings = text.split(";").map(s => s.trim()).filter(Boolean);
  return (
    <div className="space-y-1.5">
      {warnings.map((w, i) => (
        <div key={i} className="flex gap-2 rounded-md bg-amber-500/8 border border-amber-500/20 px-2.5 py-2">
          {/*<AlertTriangle className="h-3 w-3 text-amber-400 mt-0.5 shrink-0" />*/}
          <p className="text-[11px] text-amber-300/80">{w}</p>
        </div>
      ))}
    </div>
  );
}

function LinkCard({ link }: { link: SimulationLink }) {
  const shortSrc = link.source_machine.slice(-4);
  const shortTgt = link.target_machine.slice(-4);
  return (
    <div className="rounded-lg border border-border bg-muted/20 overflow-hidden">
      <div className="flex items-center gap-1.5 px-3 py-2 bg-muted/30 border-b border-border">
        {/*<Zap className="h-3 w-3 text-violet-400" />*/}
        <span className="text-[10px] text-muted-foreground">…{shortSrc}</span>
        <ChevronRight className="h-3 w-3 text-muted-foreground/50" />
        <span className="text-[10px] text-muted-foreground">…{shortTgt}</span>
      </div>
      {link.states.map((state, i) => (
        <div key={i} className="px-3 divide-y divide-border/60">
          {Object.entries(state).map(([k, v]) =>
            k !== "warnings" ? <AttributeRow key={k} label={k} value={v} /> : null
          )}
          {typeof state.warnings === "string" && state.warnings && (
            <div className="py-2">
              <WarningBlock text={state.warnings} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function FrameSection({ frame, step }: { frame: SimulationFrame, step?: number }) {
  const inputEntries = Object.entries(frame.production_line_full_input);
  const outputEntries = Object.entries(frame.production_line_full_output);

  return (
    <div className="space-y-3">
      {/* Step header */}
      <div className="flex items-center gap-2">
        {/*<div className={cn(
          "h-5 w-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0",
          frame.success
            ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/30"
            : "bg-red-500/20 text-red-400 ring-1 ring-red-500/30"
        )}>
          {frame.step}
        </div>*/}
        <span className="text-xs text-muted-foreground">Step {step}</span>
        {/* {frame.success
          ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 ml-auto" />
          : <XCircle className="h-3.5 w-3.5 text-red-400 ml-auto" />}*/}
      </div>

      <Accordion type="multiple" defaultValue={["input", "links", "output"]} className="space-y-2">
        {/* Input */}
        <AccordionItem value="input" className="border-0">
          <AccordionTrigger className="py-1.5 px-3 rounded-md bg-muted/30 hover:bg-muted/60 text-[11px] font-semibold text-muted-foreground tracking-wider hover:no-underline [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground/50">
            Input
          </AccordionTrigger>
          <AccordionContent className="pt-2 space-y-2 pb-0">
            {inputEntries.map(([id, data]) => (
              <RecordCard key={id} id={id} data={data as Record<string, unknown>} label="Input record" />
            ))}
          </AccordionContent>
        </AccordionItem>

        {/* Links */}
        <AccordionItem value="links" className="border-0">
          <AccordionTrigger className="py-1.5 px-3 rounded-md bg-muted/30 hover:bg-muted/60 text-[11px] font-semibold text-muted-foreground tracking-wider hover:no-underline [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground/50">
            Links ({frame.links.length})
          </AccordionTrigger>
          <AccordionContent className="pt-2 space-y-2 pb-0">
            {frame.links.map((link, i) => (
              <LinkCard key={i} link={link} />
            ))}
          </AccordionContent>
        </AccordionItem>

        {/* Output */}
        <AccordionItem value="output" className="border-0">
          <AccordionTrigger className="py-1.5 px-3 rounded-md bg-muted/30 hover:bg-muted/60 text-[11px] font-semibold text-muted-foreground tracking-wider hover:no-underline [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground/50">
            Output
          </AccordionTrigger>
          <AccordionContent className="pt-2 space-y-2 pb-0">
            {outputEntries.map(([id, data]) => (
              <RecordCard key={id} id={id} data={data as Record<string, unknown>} label="Output record" />
            ))}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

export function SimulationInspect({ data }: SimulationInspectProps) {
  const { setInspectedSimulationId } = useSimulationStore();
  const isRunning = data.status === SimulationStatus.RUNNING;
  const { startSimulation, stopSimulation } = useSimulationStore();
  const queryClient = useQueryClient();
  const updateSimulation = useUpdateSimulation();

  const handleToggle = () => {
    const newStatus = isRunning ? SimulationStatus.STOPPED : SimulationStatus.RUNNING;

    if (newStatus === SimulationStatus.RUNNING) {
      startSimulation(data.id, queryClient);
    } else {
      stopSimulation(data.id);
    }

    updateSimulation.mutate({
      id: data.id,
      data: { status: newStatus },
    });
  };

  const {
    data: steps,
    isLoading,
    isPending,
    isError,
    error,
    refetch: refetchSteps,
  } = useGetSimulationSteps(data.id);

  useEffect(() => {
    const interval = setInterval(() => {
      if (isRunning) {
        refetchSteps();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [isRunning, refetchSteps]);

  if (isLoading || isPending) {
    return <div>Loading...</div>
  }

  if (isError) {
    return <div>{error.message}</div>
  }

  console.log(steps);
  const simulationStep = steps[steps.length - 1];

  return (
    <div className="w-85 bg-black backdrop-blur-md flex flex-col h-[80vh] min-h-0 rounded-2xl border border-border shadow-md overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          {/*<div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-violet-500/15 border border-violet-500/30">
            <Activity size={18} className="text-violet-400" />
          </div>*/}
          <div className="min-w-0">
            <span className="font-medium block">Simulation</span>
            <span className="text-[10px] text-muted-foreground truncate block">{data.id}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {/*{statusBadge(data.status)}*/}
          {data.status === SimulationStatus.RUNNING ? <Button
            variant="outline"
            onClick={() => handleToggle()}
          >
            Stop
          </Button> : <Button
            variant="outline"
            onClick={() => handleToggle()}
          >
            Start
          </Button>}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setInspectedSimulationId(null)}
            className="h-8 w-8"
          >
            <ArrowLeft size={16} />
          </Button>
        </div>
      </div>

      <Separator className="shrink-0" />

      {/* Meta row */}
      {/*<div className="grid grid-cols-3 gap-2 px-4 py-3 shrink-0">
        {[
          { label: "Steps", value: `${simulationStep.steps_completed}/${simulationStep.steps_requested}` },
          { label: "Frames", value: simulationStep.frames.length },
          { label: "Warnings", value: allWarnings.length },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-md bg-muted/20 border border-border px-2.5 py-1.5 text-center">
            <p className="text-sm">{label}</p>
            <p className="text-sm font-semibold">{value}</p>
          </div>
        ))}
      </div>*/}

      {/* Warning summary chips */}
      {/*{allWarnings.length > 0 && (
        <div className="flex gap-2 px-4 pb-3 shrink-0">
          {criticalCount > 0 && (
            <div className="flex items-center gap-1.5 rounded-full bg-red-500/10 border border-red-500/25 px-2.5 py-1 text-[11px] text-red-400 font-semibold">
              <XCircle className="h-3 w-3" />
              {criticalCount} critical
            </div>
          )}
          {warnCount > 0 && (
            <div className="flex items-center gap-1.5 rounded-full bg-amber-500/10 border border-amber-500/25 px-2.5 py-1 text-[11px] text-amber-400 font-semibold">
              <AlertTriangle className="h-3 w-3" />
              {warnCount} warnings
            </div>
          )}
        </div>
      )}*/}

      <Separator className="shrink-0" />

      {/* Scrollable body */}
      <ScrollArea className="flex-1 min-h-0">
        {steps.length > 0 &&
          <div className="p-4 space-y-6">
            <FrameSection frame={simulationStep.frame_data} step={simulationStep.step} />
          </div>}
      </ScrollArea>

      {/*<div className="p-4 space-y-2">
        <Textarea placeholder="Let AI explain the result..." className="w-full h-20" />
        <Button className="w-full">Explain <Wand2 size={16} /></Button>
      </div>*/}
    </div>
  );
}
