import { usePipelineStore } from "~/features/pipeline/pipeline.store";
import { useGetSimulations } from "../simulations.hooks";
import { SimulationCard } from "./simulation.card";
import { Search, AlertCircle, Database } from "lucide-react";
import { Input } from "~/components/ui/input";
import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Skeleton } from "~/components/ui/skeleton";
import { useState, useMemo } from "react";

export function SimulationsList() {
  const { lineId, isSimulationPanelOpen } = usePipelineStore();
  const [searchQuery, setSearchQuery] = useState("");

  const { data: simulations, isPending, isError } = useGetSimulations(lineId);

  const filtered = useMemo(() => {
    if (!simulations) return [];
    const q = searchQuery.trim().toLowerCase();
    if (!q) return [...simulations].sort((a, b) => Number(a.id > b.id));
    return simulations
      .filter((s) => String(s.id).includes(q) || s.status.toLowerCase().includes(q))
      .sort((a, b) => Number(a.id > b.id));
  }, [simulations, searchQuery]);

  if (!isSimulationPanelOpen) return null;

  return (
    <div className="w-85 bg-card/80 backdrop-blur-md flex flex-col h-[80vh] min-h-0 rounded-2xl border border-border shadow-md overflow-hidden">
      <div className="p-4 shrink-0">
        <h2 className="text-lg font-bold mb-3">Simulation History</h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search simulations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Separator className="shrink-0" />

      <div className="flex-1 min-h-0">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-2">
            {isPending ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-border p-3 space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-20" />
                  <div className="flex gap-2 pt-1">
                    <Skeleton className="h-7 w-16" />
                    <Skeleton className="h-7 w-16" />
                    <Skeleton className="h-7 w-16 ml-auto" />
                  </div>
                </div>
              ))
            ) : isError ? (
              <div className="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/5 p-4 text-destructive text-sm">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <p>Failed to load simulations</p>
              </div>
            ) : !filtered.length ? (
              <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
                <Database className="h-8 w-8 text-muted-foreground/50" />
                <div className="space-y-1">
                  <p className="text-sm font-medium">
                    {searchQuery ? "No results found" : "No simulations yet"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {searchQuery
                      ? "Try a different search term"
                      : "Create your first simulation to begin testing."}
                  </p>
                </div>
              </div>
            ) : (
              filtered.map((simulation) => (
                <SimulationCard key={simulation.id} data={simulation} />
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
