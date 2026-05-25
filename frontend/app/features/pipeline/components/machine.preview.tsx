import { ICON_MAP } from "../pipeline.shema";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import type { MachineTypeConfig } from "../pipeline.shema";
import { Card, CardContent, CardHeader } from "~/components/ui/card";

interface MachinePreview {
  machine: MachineTypeConfig;
}

function MachinePreview({ machine }: MachinePreview) {
  const Icon = ICON_MAP[machine.icon] || ICON_MAP["Factory"];

  const hasInputs = Object.keys(machine.defaultAttributes.inputs).length > 0;
  const hasOutputs = Object.keys(machine.defaultAttributes.outputs).length > 0;

  return (
    <Card className="h-fit absolute left-full top-0 ml-4 w-72 z-50 animate-in fade-in slide-in-from-left-2 duration-300 shadow-2xl">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-4">
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-lg rotate-3"
            style={{ backgroundColor: machine.color }}
          >
            <Icon size={24} className="text-white" />
          </div>
          <div>
            <h4 className="font-bold leading-tight">{machine.name}</h4>
            <p className="text-[10px] uppercase font-black tracking-widest text-blue-500 mt-0.5">
              {machine.process}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <p className="text-xs text-muted-foreground leading-relaxed">
          {machine.description}
        </p>

        {(hasInputs || hasOutputs) && <Separator />}

        {hasInputs && (
          <div className="space-y-2">
            <p className="text-[10px] uppercase font-black text-muted-foreground tracking-tighter">
              Input Slots
            </p>
            <div className="flex flex-wrap gap-1.5">
              {Object.values(machine.defaultAttributes.inputs).map((attr) => (
                <Badge key={attr.definition.id} variant="secondary" className="text-[9px] font-bold">
                  {attr.definition.name}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {hasOutputs && (
          <div className="space-y-2">
            <p className="text-[10px] uppercase font-black text-muted-foreground tracking-tighter">
              Output Slots
            </p>
            <div className="flex flex-wrap gap-1.5">
              {Object.values(machine.defaultAttributes.outputs).map((attr) => (
                <Badge key={attr.definition.id} variant="secondary" className="text-[9px] font-bold">
                  {attr.definition.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default MachinePreview;
