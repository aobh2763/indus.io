import { Search } from "lucide-react";
import MachinePreview from "./preview";
import { useDraggable } from '@neodrag/react';
import { ICON_MAP } from "../../types/machine";
import { usePipelineStore } from "../../store/pipeline";
import { AVAILABLE_MACHINES } from "../../types/machine";
import type { MachineTypeConfig } from "../../types/machine";
import { useReactFlow, type XYPosition } from "@xyflow/react";
import { useRef, useState, useMemo, useCallback, type FC } from "react";

interface DraggableMachineProps {
  machine: MachineTypeConfig;
  onMouseLeave: () => void;
  onMouseEnter: (machine: MachineTypeConfig) => void;
  onDrop: (machine: MachineTypeConfig, position: XYPosition) => void;
}

export const DraggableMachine: FC<DraggableMachineProps> = ({ machine, onMouseEnter, onMouseLeave, onDrop }) => {
  const draggableRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState<XYPosition>({ x: 0, y: 0 });

  useDraggable(draggableRef, {
    position,

    onDrag: ({ offsetX, offsetY }) => {
      setPosition({
        x: offsetX,
        y: offsetY,
      });
    },

    onDragEnd: ({ event }) => {
      setPosition({ x: 0, y: 0 });
      onDrop(machine, {
        x: event.clientX,
        y: event.clientY,
      });
    },
  });

  const IconComponent = ICON_MAP[machine.icon] || ICON_MAP["Factory"];

  return (
    <div
      ref={draggableRef}
      onMouseEnter={() => onMouseEnter(machine)}
      onMouseLeave={onMouseLeave}
      className={`p-3 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-150 group max-w-24 cursor-grab active:cursor-grabbing`}
    >
      <div className="flex flex-col items-center gap-1">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm group-hover:shadow-md transition-shadow"
          style={{ backgroundColor: machine.color }}
        >
          <IconComponent size={20} className="text-white" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-medium text-gray-900 dark:text-white text-[11px] max-w-[80px] text-center leading-tight">
            {machine.name}
          </p>
        </div>
      </div>
    </div>
  );
};

const MachineList: FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [hoveredMachine, setHoveredMachine] = useState<MachineTypeConfig | null>(null);

  const groupedMachines = useMemo(() => {
    const filtered = !searchQuery.trim()
      ? AVAILABLE_MACHINES
      : AVAILABLE_MACHINES.filter(
        (machine) =>
          machine.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          machine.description.toLowerCase().includes(searchQuery.toLowerCase())
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

  const { addNode } = usePipelineStore();
  const { screenToFlowPosition } = useReactFlow();

  const handleNodeDrop = useCallback(
    (machine: MachineTypeConfig, screenPosition: XYPosition) => {
      const flow = document.querySelector('.react-flow');
      const flowRect = flow?.getBoundingClientRect();
      const isInFlow =
        flowRect &&
        screenPosition.x >= flowRect.left &&
        screenPosition.x <= flowRect.right &&
        screenPosition.y >= flowRect.top &&
        screenPosition.y <= flowRect.bottom;

      if (isInFlow) {
        const position = screenToFlowPosition(screenPosition);
        addNode(machine, position);
      }
    },
    [addNode, screenToFlowPosition],
  );

  return (
    <div>
      <div className="dark:bg-gray-900/80 flex flex-col backdrop-blur-md max-h-[80vh] rounded-2xl">
        <div className="p-4 border-b border-gray-100 dark:border-gray-600">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3">
            Machine Library
          </h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search components..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-gray-900 dark:text-white placeholder-gray-400 transition-all"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {!hasResults ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
              No machines found
            </p>
          ) : (
            <div className="space-y-8 pb-4">
              {Object.entries(groupedMachines).map(([process, machines]) => (
                <div key={process} className="space-y-3">
                  <div>
                    <h3 className="text-sm capitalize dark:text-gray-500">
                      {process}
                    </h3>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {machines.map((machine) => (
                      <DraggableMachine
                        key={machine.name}
                        machine={machine}
                        onDrop={handleNodeDrop}
                        onMouseEnter={setHoveredMachine}
                        onMouseLeave={() => setHoveredMachine(null)}
                      />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {hoveredMachine && <MachinePreview machine={hoveredMachine} />}
    </div>
  );
};

export default MachineList;
