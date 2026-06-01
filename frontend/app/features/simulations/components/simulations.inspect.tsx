import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { STEP, type SimulationFrame, type SimulationLink, type SimulationResponse, SimulationStatus } from "../simulations.schema";
import { simulationsApi } from "../simulations.api";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

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
      </div>
    </div>
  );
}

function ExplainModal({ text, onClose }: { text: string; onClose: () => void }) {
  const [status, setStatus] = useState<"loading" | "done" | "error">("loading");
  const [explanation, setExplanation] = useState<string>("");

  // Kick off the API call on mount
  useState(() => {
    simulationsApi.explain(text)
      .then((result: string) => {
        setExplanation(result);
        setStatus("done");
      })
      .catch(() => {
        setExplanation("Something went wrong fetching the explanation.");
        setStatus("error");
      });
  });

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      {/* Modal box — stop clicks bubbling to backdrop */}
      <div
        className="relative w-full max-w-md mx-4 rounded-xl bg-zinc-900 border border-amber-500/20 shadow-2xl p-5"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-semibold uppercase tracking-widest text-amber-400/80">
            AI Explanation
          </span>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-300 transition-colors text-lg leading-none"
          >
            ×
          </button>
        </div>

        {/* Original warning */}
        <p className="text-[11px] text-zinc-500 italic mb-4 border-l-2 border-amber-500/30 pl-2">
          {text}
        </p>

        {/* Content area */}
        {status === "loading" ? (
          <div className="flex flex-col items-center justify-center py-8 gap-3">
            <svg
              className="animate-spin h-7 w-7 text-violet-400"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
            <span className="text-xs text-zinc-500">Thinking…</span>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {/* Scrollable explanation */}
            <div className="max-h-64 overflow-y-auto pr-1">
              <div className="max-h-60 overflow-y-auto">
                <div className="text-xs text-zinc-300 leading-relaxed prose prose-invert prose-xs max-w-none
                  prose-p:my-1 prose-headings:text-zinc-200 prose-strong:text-zinc-200
                  prose-code:text-violet-300 prose-code:bg-zinc-800 prose-code:px-1 prose-code:rounded
                  prose-ul:my-1 prose-li:my-0">
                  <ReactMarkdown>{explanation}</ReactMarkdown>
                </div>
              </div>
            </div>

            {/* Always visible footer button */}
            <Button
              size="sm"
              variant="ghost"
              className="w-full h-8 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-white/5 border border-zinc-700 hover:border-zinc-500 transition-all"
              onClick={onClose}
            >
              Got it
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

function WarningBlock({ text }: { text: string }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="flex flex-col items-start rounded-md bg-amber-500/8 border border-amber-500/20 px-2.5 py-2">
        {/* Warning text */}
        <p className="text-[11px] text-amber-300/80 leading-snug text-justify">
          {text}
        </p>

        {/* Explain button */}
        <Button
          size="sm"
          variant="ghost"
          className="self-end h-6 px-2 text-[10px] text-violet-300 hover:text-violet-200 hover:bg-violet-500/10 shrink-0"
          onClick={() => setShowModal(true)}
        >
          Explain ✨
        </Button>
      </div>

      {showModal && (
        <ExplainModal text={text} onClose={() => setShowModal(false)} />
      )}
    </>
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

        {/* Warnings */}
        <AccordionItem value="warnings" className="border-0">
          <AccordionTrigger className="py-1.5 px-3 rounded-md bg-muted/30 hover:bg-muted/60 text-[11px] font-semibold text-muted-foreground tracking-wider hover:no-underline [&>svg]:h-3 [&>svg]:w-3 [&>svg]:text-muted-foreground/50">
            Warnings
          </AccordionTrigger>
          <AccordionContent className="pt-2 space-y-2 pb-0 overflow-visible">
            <div className="flex flex-col gap-2 rounded-md bg-amber-500/8 border border-amber-500/20 px-2.5 py-2">
              {(frame.errors_warnings ?? [])
                .filter((w) => w?.[0] !== '[')
                .map((w: string, i: number) => (
                  <WarningBlock key={i} text={w} />
                ))}
            </div>
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
          { label: "Warnings", value: warnCount },
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
          <div className="h-full min-h-0 p-4 space-y-6">
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
