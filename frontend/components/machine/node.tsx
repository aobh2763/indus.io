import { memo } from "react";
import { Handle, Position } from "@xyflow/react";
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
import type { MachineNodeData } from "../../store/pipeline";

const ICON_MAP: Record<string, LucideIcon> = {
  Factory,
  Hammer,
  Move3d,
  Bot,
  Scan,
  Zap,
  Wrench,
};

export interface MachineNodeComponentProps {
  data: MachineNodeData;
  selected?: boolean;
}

function MachineNodeComponent({ data, selected }: MachineNodeComponentProps) {
  const IconComponent = ICON_MAP[data.icon] || Factory;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative flex flex-col items-center gap-2">
        <Handle
          type="target"
          position={Position.Left}
        />
        <div
          className={`
            relative w-10 h-10 rounded-full flex items-center justify-center
            transition-all duration-200 shadow-md mx-2
            ${selected ? "ring-1 ring-white scale-105" : ""}
          `}
          style={{ backgroundColor: data.color }}
        >
          <IconComponent size={20} className="text-white" />
        </div>

        <Handle
          type="source"
          position={Position.Right}
        />
      </div>

      <span
        className="text-xs font-medium text-gray-700 dark:text-gray-200 max-w-[100px] text-center truncate"
        title={data.label}
      >
        {data.label}
      </span>
    </div>
  );
}

export default memo(MachineNodeComponent);
