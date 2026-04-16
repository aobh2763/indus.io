import { useState, useEffect, type FC } from "react";
import { X, Trash2, Save } from "lucide-react";
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
import { usePipelineStore, type MachineNode } from "../../store/pipeline";
import type { MachineParameter } from "../../types/machine";

const ICON_MAP: Record<string, LucideIcon> = {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
};

const ConfigPanel: FC = () => {
  const {
    isConfigPanelOpen,
    selectedNodeId,
    setConfigPanelOpen,
    getSelectedNode,
    updateNodeData,
    removeNode,
  } = usePipelineStore();

  const [localParameters, setLocalParameters] = useState<MachineParameter[]>([]);
  const [localLabel, setLocalLabel] = useState("");

  const selectedNode = getSelectedNode();

  useEffect(() => {
    if (selectedNode) {
      setLocalParameters([...selectedNode.data.parameters]);
      setLocalLabel(selectedNode.data.label);
    }
  }, [selectedNode]);

  if (!isConfigPanelOpen || !selectedNode) return null;

  const IconComponent = ICON_MAP[selectedNode.data.icon] || Factory;

  const handleSave = () => {
    updateNodeData(selectedNodeId!, {
      label: localLabel,
      parameters: localParameters,
    });
    setConfigPanelOpen(false);
  };

  const handleDelete = () => {
    removeNode(selectedNodeId!);
    setConfigPanelOpen(false);
  };

  const handleParameterChange = (index: number, value: number) => {
    setLocalParameters((prev) =>
      prev.map((param, i) =>
        i === index ? { ...param, value } : param
      )
    );
  };

  return (
    <div className="w-80 bg-gray-900 flex flex-col animate-slide-in shadow-lg border border-gray-800">
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: selectedNode.data.color }}
          >
            <IconComponent size={20} className="text-white" />
          </div>
          <span className="font-medium text-white">
            Configure
          </span>
        </div>
        <button
          onClick={() => setConfigPanelOpen(false)}
          className="p-1 rounded-lg hover:bg-gray-800 transition-colors"
        >
          <X size={20} className="text-gray-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-200 mb-1.5">
            Name
          </label>
          <input
            type="text"
            value={localLabel}
            onChange={(e) => setLocalLabel(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
          />
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-200 mb-3">
            Parameters
          </h3>
          <div className="space-y-3">
            {localParameters.map((param, index) => (
              <div key={index}>
                <label className="block text-xs text-gray-400 mb-1">
                  {param.metadata.name}
                  {param.unit && (
                    <span className="ml-1 text-gray-500">({param.unit})</span>
                  )}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={param.value}
                    onChange={(e) =>
                      handleParameterChange(index, parseFloat(e.target.value) || 0)
                    }
                    className="flex-1 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-800 flex gap-2">
        <button
          onClick={handleDelete}
          className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-400 hover:text-red-300 rounded-lg hover:bg-red-900/20 transition-colors"
        >
          <Trash2 size={16} />
          Delete
        </button>
        <button
          onClick={handleSave}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          <Save size={16} />
          Save
        </button>
      </div>
    </div>
  );
};

export default ConfigPanel;
