import { useState, useMemo, type FC } from "react";
import { useReactFlow } from "@xyflow/react";
import { Search } from "lucide-react";
import {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import { AVAILABLE_MACHINES } from "../../types/machine";
import { usePipelineStore } from "../../store/pipeline";
import type { MachineTypeConfig } from "../../types/machine";

const ICON_MAP: Record<string, LucideIcon> = {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
};

const MachineList: FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [hoveredMachine, setHoveredMachine] = useState<MachineTypeConfig | null>(null);
  const { fitView } = useReactFlow();
  const addNode = usePipelineStore((state) => state.addNode);

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

  const handleAddMachine = (machineConfig: MachineTypeConfig) => {
    addNode(machineConfig, { x: 250, y: 150 });
    setTimeout(() => fitView({ padding: 0.2, duration: 300 }), 100);
  };

  const hasResults = Object.keys(groupedMachines).length > 0;

  return (
    <div className="relative group/list">
      <div className="w-80 bg-white dark:bg-gray-900 flex flex-col max-h-[80vh] rounded-lg shadow-xl border border-gray-200 dark:border-gray-800">
        <div className="p-4 shrink-0">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Machines
          </h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search machines..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white placeholder-gray-400"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {!hasResults ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              No machines found
            </p>
          ) : (
            <div className="space-y-6 pb-4">
              {Object.entries(groupedMachines).map(([process, machines]) => (
                <div key={process} className="space-y-2">
                  <div className="px-2">
                    <h3 className="text-[10px] uppercase font-bold tracking-wider text-gray-400 dark:text-gray-500">
                      {process}
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {machines.map((machine) => {
                      const IconComponent = ICON_MAP[machine.icon] || Factory;

                      return (
                        <button
                          key={machine.name}
                          onClick={() => handleAddMachine(machine)}
                          onMouseEnter={() => setHoveredMachine(machine)}
                          onMouseLeave={() => setHoveredMachine(null)}
                          className="p-3 text-left hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-150 group max-w-24"
                        >
                          <div className="flex flex-col items-center gap-1">
                            <div
                              className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                              style={{ backgroundColor: machine.color }}
                            >
                              <IconComponent size={20} className="text-white" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center justify-between gap-2">
                                <p className="font-medium text-gray-900 dark:text-white text-sm max-w-[80px] text-center truncate">
                                  {machine.name}
                                </p>
                              </div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {hoveredMachine && (
        <div className="h-full absolute left-full top-0 ml-4 w-72 bg-white dark:bg-gray-900 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-800 p-4 z-50 animate-in fade-in slide-in-from-left-2 duration-200">
          <div className="flex items-center gap-3 mb-4">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg"
              style={{ backgroundColor: hoveredMachine.color }}
            >
              {(() => {
                const Icon = ICON_MAP[hoveredMachine.icon] || Factory;
                return <Icon size={20} className="text-white" />;
              })()}
            </div>
            <div>
              <h4 className="font-bold text-gray-900 dark:text-white leading-tight">
                {hoveredMachine.name}
              </h4>
              <p className="text-[10px] uppercase font-bold tracking-wider text-blue-500">
                {hoveredMachine.process}
              </p>
            </div>
          </div>

          <p className="text-xs text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
            {hoveredMachine.description}
          </p>

          <div className="space-y-3">
            {Object.keys(hoveredMachine.defaultAttributes.inputs).length > 0 && (
              <div>
                <p className="text-[10px] uppercase font-bold text-gray-400 mb-1 tracking-tight">
                  Inputs
                </p>
                <div className="flex flex-wrap gap-1">
                  {Object.values(hoveredMachine.defaultAttributes.inputs).map(
                    (attr) => (
                      <span
                        key={attr.definition.id}
                        className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 text-[10px] rounded text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
                      >
                        {attr.definition.name}
                      </span>
                    )
                  )}
                </div>
              </div>
            )}

            {Object.keys(hoveredMachine.defaultAttributes.outputs).length > 0 && (
              <div>
                <p className="text-[10px] uppercase font-bold text-gray-400 mb-1 tracking-tight">
                  Outputs
                </p>
                <div className="flex flex-wrap gap-1">
                  {Object.values(hoveredMachine.defaultAttributes.outputs).map(
                    (attr) => (
                      <span
                        key={attr.definition.id}
                        className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 text-[10px] rounded text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
                      >
                        {attr.definition.name}
                      </span>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MachineList;
