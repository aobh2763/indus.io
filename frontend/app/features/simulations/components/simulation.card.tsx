import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Activity, Play, Square, Eye, Trash2, Loader2 } from "lucide-react";
import { useDeleteSimulation, useUpdateSimulation } from "../simulations.hooks";
import { SimulationStatus, type SimulationResponse } from "../simulations.schema";

export interface SimulationCardProps {
  data: SimulationResponse;
}

export function SimulationCard({ data }: SimulationCardProps) {
  const updateSimulation = useUpdateSimulation();
  const deleteSimulation = useDeleteSimulation();
  const isRunning = data.status === SimulationStatus.RUNNING;

  const handleToggle = () => {
    updateSimulation.mutate({
      id: data.id,
      data: {
        status: isRunning ? SimulationStatus.STOPPED : SimulationStatus.RUNNING,
      },
    });
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
