import {
  Panel,
  ReactFlow,
  Background,
  type OnSelectionChangeFunc,
} from "@xyflow/react";

import { useCallback } from "react";
import MachineNode from "./machine/node";
import MachineList from "./machine/list";
import ConfigPanel from "./machine/config-panel";
import { DragDropProvider } from "@dnd-kit/react";
import { usePipelineStore } from "../store/pipeline";

const PipelineBuilder = () => {
  const {
    nodes,
    edges,
    onConnect,
    onNodesChange,
    onEdgesChange,
    setSelectedNode,
    setDragNDropPosition
  } = usePipelineStore();

  const onSelectionChange: OnSelectionChangeFunc = useCallback(({ nodes: selectedNodes }) => {
    if (selectedNodes.length === 1) {
      setSelectedNode(selectedNodes[0].id);
    } else {
      setSelectedNode(null);
    }
  }, [setSelectedNode]);

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
          </Panel>
        </ReactFlow>
      </div>
    </DragDropProvider>
  );
};

export default PipelineBuilder;
