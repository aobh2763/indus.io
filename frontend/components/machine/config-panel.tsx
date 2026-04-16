import { useState, useEffect, type FC } from "react";
import { X, Trash2, Save, ChevronDown, ChevronRight } from "lucide-react";
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
import { usePipelineStore } from "../../store/pipeline";
import type { ProcessAttributes, AttributeInstance } from "../../types/machine";

const ICON_MAP: Record<string, LucideIcon> = {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
};

type LayerKey = "inputs" | "configs" | "outputs";

const LAYER_LABELS: Record<LayerKey, { title: string; description: string }> = {
  inputs: { title: "Inputs", description: "Input material attributes" },
  configs: { title: "Configuration", description: "Configurable parameters" },
  outputs: { title: "Outputs", description: "Output product attributes" },
};

function AttributeField({
  attrKey,
  attr,
  onChange,
}: {
  attrKey: string;
  attr: AttributeInstance;
  onChange: (key: string, value: any) => void;
}) {
  const { definition, value } = attr;

  if (definition.type === "number") {
    return (
      <div>
        <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
          {definition.name}
          {definition.unit && (
            <span className="ml-1 text-gray-400">({definition.unit})</span>
          )}
        </label>
        <input
          type="number"
          value={value}
          onChange={(e) =>
            onChange(attrKey, parseFloat(e.target.value) || 0)
          }
          className="w-full px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
        />
      </div>
    );
  }

  if (definition.type === "boolean") {
    return (
      <div className="flex items-center justify-between">
        <label className="text-xs text-gray-500 dark:text-gray-400">
          {definition.name}
        </label>
        <input
          type="checkbox"
          checked={!!value}
          onChange={(e) => onChange(attrKey, e.target.checked)}
          className="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
        />
      </div>
    );
  }

  // string / enum / fallback
  return (
    <div>
      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
        {definition.name}
      </label>
      {definition.type === "enum" && definition.options ? (
        <select
          value={value}
          onChange={(e) => onChange(attrKey, e.target.value)}
          className="w-full px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
        >
          <option value="">Select...</option>
          {definition.options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(attrKey, e.target.value)}
          className="w-full px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
        />
      )}
    </div>
  );
}

function AttributeSection({
  layerKey,
  attributes,
  onChange,
}: {
  layerKey: LayerKey;
  attributes: Record<string, AttributeInstance>;
  onChange: (layer: LayerKey, key: string, value: any) => void;
}) {
  const [expanded, setExpanded] = useState(true);
  const entries = Object.entries(attributes);
  const { title, description } = LAYER_LABELS[layerKey];

  if (entries.length === 0) {
    return (
      <div className="opacity-50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {title}
          </span>
        </div>
        <p className="text-xs text-gray-400 italic">No attributes defined yet</p>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full text-left mb-2"
      >
        {expanded ? (
          <ChevronDown size={14} className="text-gray-400" />
        ) : (
          <ChevronRight size={14} className="text-gray-400" />
        )}
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {title}
        </span>
        <span className="text-[10px] text-gray-400 ml-auto">
          {entries.length} attr{entries.length !== 1 ? "s" : ""}
        </span>
      </button>
      {expanded && (
        <div className="space-y-3 pl-5">
          {entries.map(([key, attr]) => (
            <AttributeField
              key={key}
              attrKey={key}
              attr={attr}
              onChange={(k, v) => onChange(layerKey, k, v)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

const ConfigPanel: FC = () => {
  const {
    isConfigPanelOpen,
    selectedNodeId,
    setConfigPanelOpen,
    getSelectedNode,
    updateNodeData,
    removeNode,
  } = usePipelineStore();

  const [localAttributes, setLocalAttributes] = useState<ProcessAttributes>({
    inputs: {},
    configs: {},
    outputs: {},
  });
  const [localLabel, setLocalLabel] = useState("");

  const selectedNode = getSelectedNode();

  useEffect(() => {
    if (selectedNode) {
      setLocalAttributes(
        JSON.parse(JSON.stringify(selectedNode.data.attributes))
      );
      setLocalLabel(selectedNode.data.label);
    }
  }, [selectedNode]);

  if (!isConfigPanelOpen || !selectedNode) return null;

  const IconComponent = ICON_MAP[selectedNode.data.icon] || Factory;

  const handleSave = () => {
    updateNodeData(selectedNodeId!, {
      label: localLabel,
      attributes: localAttributes,
    });
    setConfigPanelOpen(false);
  };

  const handleDelete = () => {
    removeNode(selectedNodeId!);
    setConfigPanelOpen(false);
  };

  const handleAttributeChange = (layer: LayerKey, key: string, value: any) => {
    setLocalAttributes((prev) => ({
      ...prev,
      [layer]: {
        ...prev[layer],
        [key]: {
          ...prev[layer][key],
          value,
        },
      },
    }));
  };

  return (
    <div className="w-80 bg-white dark:bg-gray-900 flex flex-col animate-slide-in rounded-lg max-h-[80vh]">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 shrink-0">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ backgroundColor: selectedNode.data.color }}
          >
            <IconComponent size={20} className="text-white" />
          </div>
          <div>
            <span className="font-medium text-gray-900 dark:text-white block">
              Configure
            </span>
            <span className="text-[10px] uppercase font-bold text-gray-400">
              {selectedNode.data.process}
            </span>
          </div>
        </div>
        <button
          onClick={() => setConfigPanelOpen(false)}
          className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <X size={20} className="text-gray-500" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
            Name
          </label>
          <input
            type="text"
            value={localLabel}
            onChange={(e) => setLocalLabel(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
          />
        </div>

        <hr className="border-gray-200 dark:border-gray-700" />

        {(["configs"] as LayerKey[]).map((layer) => (
          <AttributeSection
            key={layer}
            layerKey={layer}
            attributes={localAttributes[layer]}
            onChange={handleAttributeChange}
          />
        ))}
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-2 shrink-0">
        <button
          onClick={handleDelete}
          className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors bg-red-600 text-white"
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
