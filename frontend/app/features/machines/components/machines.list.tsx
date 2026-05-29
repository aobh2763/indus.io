import { useReactFlow } from "@xyflow/react";
import { useDraggable } from "@dnd-kit/react";
import MachinePreview from "./machines.preview";
import { ICON_MAP } from "~/features/pipeline/pipeline.schema";
import { usePipelineStore } from "~/features/pipeline/pipeline.store";
import { AVAILABLE_MACHINES } from "~/features/pipeline/pipeline.schema";
import { useState, useMemo, useCallback, type FC, useEffect } from "react";
import type { MachineTypeConfig } from "~/features/pipeline/pipeline.schema";

import { Search } from "lucide-react";
import { Input } from "~/components/ui/input";
import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";

interface DraggableMachineProps {
  onMouseLeave: () => void;
  machine: MachineTypeConfig;
  onDrop: (machine: MachineTypeConfig) => void;
  onMouseEnter: (machine: MachineTypeConfig) => void;
}

export const DraggableMachine: FC<DraggableMachineProps> = ({
  machine,
  onMouseEnter,
  onMouseLeave,
  onDrop,
}) => {
  const { ref, isDropping } = useDraggable({
    id: machine.name,
  });

  const IconComponent = ICON_MAP[machine.icon] || ICON_MAP["Factory"];

  useEffect(() => {
    if (isDropping) {
      onDrop(machine);
    }
  }, [isDropping, machine, onDrop]);

  return (
    <div
      ref={ref}
      onMouseEnter={() => onMouseEnter(machine)}
      onMouseLeave={onMouseLeave}
      className="p-3 text-left hover:bg-accent rounded-lg transition-all duration-150 group max-w-24 cursor-grab active:cursor-grabbing shrink-0"
    >
      <div className="flex flex-col items-center gap-1">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm group-hover:shadow-md transition-shadow"
          style={{ backgroundColor: machine.color }}
        >
          <IconComponent size={20} className="text-white" />
        </div>

        <p className="font-medium text-foreground text-[11px] max-w-[80px] text-center leading-tight break-words">
          {machine.name}
        </p>
      </div>
    </div>
  );
};

const MachineList: FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [hoveredMachine, setHoveredMachine] =
    useState<MachineTypeConfig | null>(null);

  const groupedMachines = useMemo(() => {
    const filtered = !searchQuery.trim()
      ? AVAILABLE_MACHINES
      : AVAILABLE_MACHINES.filter(
        (machine) =>
          machine.name
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          machine.description
            .toLowerCase()
            .includes(searchQuery.toLowerCase())
      );

    const groups: Record<string, MachineTypeConfig[]> = {};

    filtered.forEach((machine) => {
      if (!groups[machine.process]) {
        groups[machine.process] = [];
      }

      groups[machine.process].push(machine);
    });

    return groups;
  }, [searchQuery]);

  const hasResults = Object.keys(groupedMachines).length > 0;

  const {
    addNode,
    getDragNDropPosition,
    setDragNDropPosition,
    isMachineLibraryOpen,
  } = usePipelineStore();

  const { screenToFlowPosition } = useReactFlow();

  const handleNodeDrop = useCallback(
    (machine: MachineTypeConfig) => {
      const screenPosition = getDragNDropPosition() || {
        x: 0,
        y: 0,
      };

      setDragNDropPosition(null);

      const flow = document.querySelector(".react-flow");

      const flowRect = flow?.getBoundingClientRect();

      const isInFlow =
        flowRect &&
        screenPosition.x >= flowRect.left &&
        screenPosition.x <= flowRect.right &&
        screenPosition.y >= flowRect.top &&
        screenPosition.y <= flowRect.bottom;

      if (isInFlow) {
        addNode(machine, screenToFlowPosition(screenPosition));
      }
    },
    [
      addNode,
      getDragNDropPosition,
      screenToFlowPosition,
      setDragNDropPosition,
    ]
  );

  if (!isMachineLibraryOpen) return null;

  return (
    <div className="relative">
      <div className="bg-card/80 backdrop-blur-md flex flex-col h-[80vh] min-h-0 rounded-2xl border border-border shadow-md overflow-hidden">
        {/* Header */}
        <div className="p-4 shrink-0">
          <h2 className="text-lg font-bold mb-3">
            Machine Library
          </h2>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />

            <Input
              placeholder="Search components..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        <Separator className="shrink-0" />

        {/* Scrollable Machine List */}
        <div className="flex-1 min-h-0">
          <ScrollArea className="h-full">
            <div className="p-4">
              {!hasResults ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No machines found
                </p>
              ) : (
                <div className="space-y-6 pb-4">
                  {Object.entries(groupedMachines).map(
                    ([process, machines], index, arr) => (
                      <div
                        key={process}
                        className="space-y-3"
                      >
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                          {process}
                        </h3>

                        <div className="flex flex-wrap gap-2">
                          {machines.map((machine) => (
                            <DraggableMachine
                              key={machine.name}
                              machine={machine}
                              onDrop={handleNodeDrop}
                              onMouseEnter={setHoveredMachine}
                              onMouseLeave={() =>
                                setHoveredMachine(null)
                              }
                            />
                          ))}
                        </div>

                        {index < arr.length - 1 && (
                          <Separator className="mt-4" />
                        )}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>

      {hoveredMachine && (
        <MachinePreview machine={hoveredMachine} />
      )}
    </div>
  );
};

export default MachineList;
