import { ICON_MAP } from "../../types/machine";
import type { MachineTypeConfig } from "../../types/machine";

interface MachinePreview {
  machine: MachineTypeConfig;
}

function MachinePreview({ machine }) {
  return (
    <div className="h-fit absolute left-full top-0 ml-4 w-72 bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-800 p-5 z-50 animate-in fade-in slide-in-from-left-2 duration-300">
      <div className="flex items-center gap-4 mb-4">
        <div
          className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-lg rotate-3"
          style={{ backgroundColor: machine.color }}
        >
          {(() => {
            const Icon = ICON_MAP[machine.icon] || ICON_MAP["Factory"];
            return <Icon size={24} className="text-white" />;
          })()}
        </div>
        <div>
          <h4 className="font-bold text-gray-900 dark:text-white leading-tight">
            {machine.name}
          </h4>
          <p className="text-[10px] uppercase font-black tracking-widest text-blue-500 mt-0.5">
            {machine.process}
          </p>
        </div>
      </div>

      <p className="text-xs text-gray-600 dark:text-gray-400 mb-5 leading-relaxed">
        {machine.description}
      </p>

      <div className="space-y-4">
        {Object.keys(machine.defaultAttributes.inputs).length > 0 && (
          <div>
            <p className="text-[10px] uppercase font-black text-gray-400 mb-2 tracking-tighter">
              Input Slots
            </p>
            <div className="flex flex-wrap gap-1.5">
              {Object.values(machine.defaultAttributes.inputs).map(
                (attr) => (
                  <span
                    key={attr.definition.id}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-800/50 text-[9px] font-bold rounded-lg text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
                  >
                    {attr.definition.name}
                  </span>
                )
              )}
            </div>
          </div>
        )}

        {Object.keys(machine.defaultAttributes.outputs).length > 0 && (
          <div>
            <p className="text-[10px] uppercase font-black text-gray-400 mb-2 tracking-tighter">
              Output Slots
            </p>
            <div className="flex flex-wrap gap-1.5">
              {Object.values(machine.defaultAttributes.outputs).map(
                (attr) => (
                  <span
                    key={attr.definition.id}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-800/50 text-[9px] font-bold rounded-lg text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700"
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
  );
}

export default MachinePreview;
