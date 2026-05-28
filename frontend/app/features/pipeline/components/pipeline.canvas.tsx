import {
  Panel,
  ReactFlow,
  Background,
  type OnSelectionChangeFunc,
} from "@xyflow/react";

import { useCallback, useEffect } from "react";
import { DragDropProvider } from "@dnd-kit/react";
import { usePipelineStore } from "../pipeline.store";
import { DEFAULT_LINE_ID } from "../pipeline.schema";
import MachineNode from "~/features/machines/components/machines.node";
import MachineList from "~/features/machines/components/machines.list";
import ConfigPanel from "~/features/machines/components/machines.config";
import { Loader2 } from "lucide-react";
import { SimulationsControls } from "~/features/simulations/components/simulations.controls";
import { SimulationsList } from "~/features/simulations/components/simulations.list";

const PipelineBuilder = () => {
  const {
    nodes,
    edges,
    onConnect,
    onNodesChange,
    onEdgesChange,
    setSelectedNode,
    setDragNDropPosition,
    loadPipeline,
    isLoading,
  } = usePipelineStore();

  useEffect(() => {
    loadPipeline(DEFAULT_LINE_ID);
  }, [loadPipeline]);

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

          fitView
          style={{ background: "#000" }}
          fitViewOptions={{ padding: 0.2 }}
          proOptions={{ hideAttribution: true }}
          nodeTypes={{ machineNode: MachineNode }}
        >
          <Background />

          <Panel position="center-left">
            <MachineList />
          </Panel>

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
