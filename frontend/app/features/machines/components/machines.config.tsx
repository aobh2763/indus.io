import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { X, Trash2, Save } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Checkbox } from "~/components/ui/checkbox";
import { useState, useEffect, type FC } from "react";
import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { ICON_MAP } from "~/features/pipeline/pipeline.schema";
import { usePipelineStore } from "~/features/pipeline/pipeline.store";
import type { ProcessAttributes, AttributeInstance } from "~/features/pipeline/pipeline.schema";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "~/components/ui/collapsible";
import { ChevronDown, ChevronRight } from "lucide-react";

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

  if (definition.type === "boolean") {
    return (
      <div className="flex items-center justify-between">
        <Label className="text-xs text-muted-foreground">{definition.name}</Label>
        <Checkbox
          checked={!!value}
          onCheckedChange={(checked) => onChange(attrKey, checked)}
        />
      </div>
    );
  }

  if (definition.type === "enum" && definition.options) {
    return (
      <div className="space-y-1">
        <Label className="text-xs text-muted-foreground">{definition.name}</Label>
        <Select value={value} onValueChange={(v) => onChange(attrKey, v)}>
          <SelectTrigger className="h-8 text-sm">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {definition.options.map((opt) => (
              <SelectItem key={opt} value={opt}>
                {opt}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <Label className="text-xs text-muted-foreground">
        {definition.name}
        {definition.unit && (
          <span className="ml-1 text-muted-foreground/60">({definition.unit})</span>
        )}
      </Label>
      <Input
        type={definition.type === "number" ? "number" : "text"}
        value={value}
        onChange={(e) =>
          onChange(
            attrKey,
            definition.type === "number"
              ? parseFloat(e.target.value) || 0
              : e.target.value
          )
        }
        className="h-8 text-sm"
      />
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
  const [open, setOpen] = useState(true);
  const entries = Object.entries(attributes);
  const { title } = LAYER_LABELS[layerKey];

  if (entries.length === 0) {
    return (
      <div className="opacity-50 space-y-1">
        <span className="text-sm font-medium">{title}</span>
        <p className="text-xs text-muted-foreground italic">No attributes defined yet</p>
      </div>
    );
  }

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex items-center gap-2 w-full text-left mb-2 group">
        {open ? (
          <ChevronDown size={14} className="text-muted-foreground" />
        ) : (
          <ChevronRight size={14} className="text-muted-foreground" />
        )}
        <span className="text-sm font-medium">{title}</span>
        <span className="text-[10px] text-muted-foreground ml-auto">
          {entries.length} attr{entries.length !== 1 ? "s" : ""}
        </span>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-3 pl-5">
        {entries.map(([key, attr]) => (
          <AttributeField
            key={key}
            attrKey={key}
            attr={attr}
            onChange={(k, v) => onChange(layerKey, k, v)}
          />
        ))}
      </CollapsibleContent>
    </Collapsible>
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
      setLocalAttributes(selectedNode.data.attributes);
      setLocalLabel(selectedNode.data.label);
    }
  }, [selectedNode]);

  if (!isConfigPanelOpen || !selectedNode) return null;

  const IconComponent = ICON_MAP[selectedNode.data.icon] || ICON_MAP["Factory"];

  const handleSave = () => {
    updateNodeData(selectedNodeId!, { label: localLabel, attributes: localAttributes });
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
        [key]: { ...prev[layer][key], value },
      },
    }));
  };

  return (
    <div className="w-85 bg-black backdrop-blur-md flex flex-col h-[80vh] min-h-0 rounded-2xl border border-border shadow-md overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 shrink-0">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
            style={{ backgroundColor: selectedNode.data.color }}
          >
            <IconComponent size={20} className="text-white" />
          </div>
          <div>
            <span className="font-medium block">Configure</span>
            <span className="text-[10px] uppercase font-bold text-muted-foreground">
              {selectedNode.data.process}
            </span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setConfigPanelOpen(false)}
          className="h-8 w-8"
        >
          <X size={16} />
        </Button>
      </div>

      <Separator />

      {/* Body */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="p-4 space-y-5">
          <div className="space-y-1.5">
            <Label>Name</Label>
            <Input
              value={localLabel}
              onChange={(e) => setLocalLabel(e.target.value)}
            />
          </div>

          <Separator />

          {(["inputs", "configs", "outputs"] as LayerKey[]).map((layer) => (
            <AttributeSection
              key={layer}
              layerKey={layer}
              attributes={localAttributes[layer]}
              onChange={handleAttributeChange}
            />
          ))}
        </div>
      </ScrollArea>

      <Separator />

      {/* Footer */}
      <div className="p-4 flex gap-2 shrink-0">
        <Button variant="outline" onClick={handleDelete} className="gap-2">
          <Trash2 size={16} />
          Delete
        </Button>
        <Button onClick={handleSave} className="flex-1 gap-2">
          <Save size={16} />
          Save
        </Button>
      </div>
    </div>
  );
};

export default ConfigPanel;
