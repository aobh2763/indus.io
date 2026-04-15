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
  const { fitView } = useReactFlow();
  const addNode = usePipelineStore((state) => state.addNode);

  const filteredMachines = useMemo(() => {
    if (!searchQuery.trim()) return AVAILABLE_MACHINES;
    const query = searchQuery.toLowerCase();
    return AVAILABLE_MACHINES.filter(
      (machine) =>
        machine.name.toLowerCase().includes(query) ||
        machine.description.toLowerCase().includes(query)
    );
  }, [searchQuery]);

  const handleAddMachine = (machineConfig: MachineTypeConfig) => {
    addNode(machineConfig, { x: 250, y: 150 });
    setTimeout(() => fitView({ padding: 0.2, duration: 300 }), 100);
  };

  return (
    <div className="w-72 bg-black rounded-lg">
      <div className="p-4">
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
        {filteredMachines.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
            No machines found
          </p>
        ) : (
          <div className="space-y-2">
            {filteredMachines.map((machine) => {
              const IconComponent = ICON_MAP[machine.icon] || Factory;

              return (
                <button
                  key={machine.type}
                  onClick={() => handleAddMachine(machine)}
                  className="w-full p-3 text-left bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors duration-150 group"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                      style={{ backgroundColor: machine.color }}
                    >
                      <IconComponent size={20} className="text-white" />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white text-sm truncate">
                        {machine.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mt-0.5">
                        {machine.description}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MachineList;
