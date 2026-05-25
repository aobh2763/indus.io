import { Link } from "react-router";
import { Factory, ArrowRight } from "lucide-react";
import { ReactFlow, Background } from "@xyflow/react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import type { Machine, Connection } from "../../types/dashboard";

interface PipelinePreviewProps {
  machines: Machine[];
  connections: Connection[];
}

const MACHINE_COLORS: Record<string, string> = {
  cnc: "#3B82F6",
  press: "#EF4444",
  conveyor: "#22C55E",
  robot: "#8B5CF6",
  scanner: "#06B6D4",
  welder: "#F59E0B",
  assembler: "#EC4899",
};

export function PipelinePreview({ machines, connections }: PipelinePreviewProps) {
  // Map backend machines to ReactFlow nodes
  const nodes = machines.map((m) => ({
    id: m.id,
    position: { x: m.position_x || 0, y: m.position_y || 0 },
    data: { label: m.name },
    style: {
      background: "#000000",
      border: `1px solid ${MACHINE_COLORS[m.process || "cnc"] || "#3B82F6"}`,
      color: "#f3f4f6",
      borderRadius: "8px",
      fontSize: "11px",
      padding: "6px 12px",
      minWidth: "100px",
      textAlign: "center" as const,
      boxShadow: `0 4px 12px ${MACHINE_COLORS[m.process || "cnc"] || "#3B82F6"}20`,
    },
  }));

  // Map backend connections to ReactFlow edges
  const edges = connections.map((c) => ({
    id: c.id,
    source: c.source_machine_id,
    target: c.target_machine_id,
    animated: true,
    style: { stroke: "#6b7280", strokeWidth: 1.5 },
  }));

  // Mock data if empty
  const displayNodes = nodes.length > 0 ? nodes : [
    { id: "1", position: { x: 50, y: 50 }, data: { label: "Raw Material" }, style: { background: "#000000", color: "#fff", border: "1px solid #10b981", borderRadius: "8px", padding: "6px 12px", fontSize: "11px" } },
    { id: "2", position: { x: 220, y: 50 }, data: { label: "CNC Mill" }, style: { background: "#000000", color: "#fff", border: "1px solid #3b82f6", borderRadius: "8px", padding: "6px 12px", fontSize: "11px" } },
    { id: "3", position: { x: 390, y: 50 }, data: { label: "Assembly" }, style: { background: "#000000", color: "#fff", border: "1px solid #f59e0b", borderRadius: "8px", padding: "6px 12px", fontSize: "11px" } },
  ];

  const displayEdges = edges.length > 0 ? edges : [
    { id: "e1", source: "1", target: "2", animated: true, style: { stroke: "#6b7280" } },
    { id: "e2", source: "2", target: "3", animated: true, style: { stroke: "#6b7280" } },
  ];

  return (
    <Card className="flex flex-col h-[350px]">
      <CardHeader className="pb-3 z-10">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-cyan-500/10">
              <Factory className="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <CardTitle className="text-base">Production Pipeline</CardTitle>
              <CardDescription>Digital twin layout</CardDescription>
            </div>
          </div>
          <Link 
            to="/pipeline-builder" 
            className="text-xs font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors bg-emerald-500/10 px-2 py-1 rounded-md"
          >
            Builder <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 p-0 relative overflow-hidden rounded-b-xl border-t border-neutral-800">
        <div className="absolute inset-0 bg-black">
          <ReactFlow 
            nodes={displayNodes} 
            edges={displayEdges} 
            fitView 
            proOptions={{ hideAttribution: true }}
            panOnScroll={false}
            zoomOnScroll={false}
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable={false}
          >
            <Background color="#333333" gap={16} variant="dots" />
          </ReactFlow>
        </div>
        {/* Click overlay to navigate */}
        <Link 
          to="/pipeline-builder"
          className="absolute inset-0 z-20 cursor-pointer hover:bg-white/5 transition-colors"
          title="Click to edit pipeline"
        />
      </CardContent>
    </Card>
  );
}
