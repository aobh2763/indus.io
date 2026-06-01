import {
  Panel,
  ReactFlow,
  Background,
  type OnSelectionChangeFunc,
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type EdgeProps,
} from "@xyflow/react";

import { Loader2, X } from "lucide-react";
import { useCallback, useEffect } from "react";
import { DragDropProvider } from "@dnd-kit/react";
import { usePipelineStore } from "../pipeline.store";
import MachineNode from "~/features/machines/components/machines.node";
import MachineList from "~/features/machines/components/machines.list";
import ConfigPanel from "~/features/machines/components/machines.config";
import { SimulationsList } from "~/features/simulations/components/simulations.list";
import { SimulationsControls } from "~/features/simulations/components/simulations.controls";

const DeletableEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
}: EdgeProps) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const removeEdge = usePipelineStore((state) => state.removeEdge);
  const isReadOnly = usePipelineStore((state) => state.isReadOnly);

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
      <EdgeLabelRenderer>
        <div
          style={{
            opacity: 0.8,
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: "all",
          }}
          className="nodrag nopan"
        >
          {!isReadOnly && (
            <button
              className="flex h-2 w-2 cursor-pointer items-center justify-center rounded-full border border-neutral-700 bg-neutral-900 text-neutral-400 transition-colors hover:border-red-500 hover:bg-red-500 hover:text-white"
              onClick={() => removeEdge(id)}
            >
              <X className="h-1 w-1" />
            </button>
          )}
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

const edgeTypes = {
  deletableEdge: DeletableEdge,
};

const PipelineBuilder = () => {
  const {
    nodes,
    edges,
    lineId,
    isLoading,
    isReadOnly,
    onConnect,
    onNodesChange,
    onEdgesChange,
    setSelectedNode,
    setDragNDropPosition,
    loadPipeline,
  } = usePipelineStore();

  useEffect(() => {
    if (lineId) {
      loadPipeline(lineId);
    }
  }, [lineId, loadPipeline]);

  const onSelectionChange: OnSelectionChangeFunc = useCallback(({ nodes: selectedNodes }) => {
    if (selectedNodes.length === 1) {
      setSelectedNode(selectedNodes[0].id);
    } else {
      setSelectedNode(null);
    }
  }, [setSelectedNode]);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Loading pipeline...</p>
        </div>
      </div>
    );
  }

  return (
    <DragDropProvider
      onDragEnd={(event) => {
        if (event.canceled) return;
        const { position } = event.operation;
        setDragNDropPosition({ x: position.current.x, y: position.current.y });
      }}
    >
      <div className="h-screen">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onConnect={onConnect}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onSelectionChange={onSelectionChange}
          nodesDraggable={!isReadOnly}
          nodesConnectable={!isReadOnly}
          edgesReconnectable={!isReadOnly}
          elementsSelectable

          fitView
          style={{ background: "#000" }}
          fitViewOptions={{ padding: 0.2 }}
          proOptions={{ hideAttribution: true }}
          nodeTypes={{ machineNode: MachineNode }}
          edgeTypes={edgeTypes}
        >
          <Background />

          <Panel position="center-left">
            {!isReadOnly && <MachineList />}
          </Panel>

          {isReadOnly && (
            <Panel position="top-center">
              <div className="rounded-lg border border-neutral-800 bg-black/80 px-3 py-1.5 text-xs text-neutral-300 shadow-lg">
                View-only pipeline
              </div>
            </Panel>
          )}

          <Panel position="center-right">
            <ConfigPanel />
            <SimulationsList />
          </Panel>

          <Panel position="bottom-center">
            <SimulationsControls />
          </Panel>
        </ReactFlow>
      </div>
    </DragDropProvider>
  );
};

export default PipelineBuilder;
