import { memo } from "react";
import { ICON_MAP } from "../../types/machine";
import { Handle, Position } from "@xyflow/react";
import type { MachineNodeData } from "../../store/pipeline";

export interface MachineNodeComponentProps {
  data: MachineNodeData;
  selected?: boolean;
}

function MachineNodeComponent({ data, selected }: MachineNodeComponentProps) {
  const IconComponent = ICON_MAP[data.icon] || ICON_MAP["Factory"];

  return (
    <div className={`flex flex-col items-center ${selected ? "gap-1" : ""}`}>
      <div className="relative flex flex-col items-center gap-1">
        <div
          className={`
            relative w-10 h-10 rounded-full flex items-center justify-center
            transition-all duration-200 shadow-md
            ${selected ? "ring-1 ring-white scale-105 mx-0.5" : ""}
          `}
          style={{ backgroundColor: data.color }}
        >
          <IconComponent size={20} className="text-white" />
        </div>

        <Handle
          type="target"
          position={Position.Left}
        />

        <Handle
          type="source"
          position={Position.Right}
        />
      </div>

      <span
        style={{ fontSize: 8 }}
        className="text-gray-700 dark:text-gray-200 max-w-[100px] text-center truncate"
        title={data.label}
      >
        {data.label}
      </span>
    </div>
  );
}

export default memo(MachineNodeComponent);
