import {
  Panel,
  ReactFlow,
  Background,
  type OnSelectionChangeFunc,
} from "@xyflow/react";

import { Loader2 } from "lucide-react";
import { useCallback, useEffect } from "react";
import { DragDropProvider } from "@dnd-kit/react";
import { usePipelineStore } from "../pipeline.store";
import MachineNode from "~/features/machines/components/machines.node";
import MachineList from "~/features/machines/components/machines.list";
import ConfigPanel from "~/features/machines/components/machines.config";
import { SimulationsList } from "~/features/simulations/components/simulations.list";
import { SimulationsControls } from "~/features/simulations/components/simulations.controls";

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
