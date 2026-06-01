import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { useSimulationStore } from "../simulations.store";
import { Activity, Play, Square, Eye, Trash2, Loader2 } from "lucide-react";
import { useDeleteSimulation, useUpdateSimulation } from "../simulations.hooks";
import { SimulationStatus, type SimulationResponse } from "../simulations.schema";
import { useQueryClient } from "@tanstack/react-query";

export interface SimulationCardProps {
  data: SimulationResponse;
}

export function SimulationCard({ data }: SimulationCardProps) {
  const updateSimulation = useUpdateSimulation();
  const deleteSimulation = useDeleteSimulation();
  const isRunning = data.status === SimulationStatus.RUNNING;
  const { startSimulation, stopSimulation } = useSimulationStore();

  const queryClient = useQueryClient();
  const { setInspectedSimulationId } = useSimulationStore();

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

  const handleInspect = () => {
    setInspectedSimulationId(data.id);
  };

  const handleDelete = () => {
    deleteSimulation.mutate(data.id);
  };

  return (
    <div className="rounded-xl border border-border bg-card hover:bg-accent/40 transition-colors duration-150 p-3 space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-foreground">
          Simulation #{data.id}
        </p>
        <Badge
          variant={isRunning ? "default" : "secondary"}
          className="capitalize text-[11px] gap-1 px-2 py-0.5"
        >
          <Activity className="h-3 w-3" />
          {data.status}
        </Badge>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        <Button
          size="sm"
          onClick={handleToggle}
          disabled={updateSimulation.isPending}
          className="h-7 gap-1.5 text-xs px-2.5"
        >
          {updateSimulation.isPending ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : isRunning ? (
            <Square className="h-3 w-3" />
          ) : (
            <Play className="h-3 w-3" />
          )}
          {isRunning ? "Stop" : "Start"}
        </Button>

        <Button
          size="sm"
          variant="secondary"
          className="h-7 gap-1.5 text-xs px-2.5"
          onClick={handleInspect}
        >
          <Eye className="h-3 w-3" />
          Inspect
        </Button>

        <Button
          size="sm"
          variant="destructive"
          className="h-7 gap-1.5 text-xs px-2.5"
          onClick={handleDelete}
          disabled={deleteSimulation.isPending}
        >
          {deleteSimulation.isPending ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Trash2 className="h-3 w-3" />
          )}
          Delete
        </Button>
      </div>
    </div>
  );
}
