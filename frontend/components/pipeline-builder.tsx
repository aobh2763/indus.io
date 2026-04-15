import { type FC, useCallback, useMemo } from "react";
import { ReactFlow, Background, Controls, MiniMap, type OnSelectionChangeFunc, Panel, ReactFlowProvider } from "@xyflow/react";
import { useShallow } from "zustand/react/shallow";
import { usePipelineStore } from "../store/pipeline";
import MachineNode from "./machine/node";
import MachineList from "./machine/list";
import ConfigPanel from "./machine/config-panel";

const nodeTypes = {
  machineNode: MachineNode,
};

const PipelineBuilder: FC = () => {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    setSelectedNode,
  } = usePipelineStore(
    useShallow((state) => ({
      nodes: state.nodes,
      edges: state.edges,
      onNodesChange: state.onNodesChange,
      onEdgesChange: state.onEdgesChange,
      onConnect: state.onConnect,
      setSelectedNode: state.setSelectedNode,
    }))
  );

  const onSelectionChange: OnSelectionChangeFunc = useCallback(({ nodes: selectedNodes }) => {
    if (selectedNodes.length === 1) {
      setSelectedNode(selectedNodes[0].id);
    } else {
      setSelectedNode(null);
    }
  }, [setSelectedNode]);

  const fitViewOptions = useMemo(() => ({ padding: 0.2 }), []);

  return (
    <div className="w-full h-screen flex bg-gray-50 dark:bg-gray-950">
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onSelectionChange={onSelectionChange}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={fitViewOptions}
        >
          <Panel position="top-left">
            <MachineList />
          </Panel>
          <Background gap={16} color="#e5e7eb" className="dark:!bg-gray-950" />
          <Controls className="dark:fill-gray-300 [&>button]:dark:bg-gray-800 [&>button]:dark:border-gray-700 [&>button]:dark:text-gray-300" />
          <MiniMap
            className="dark:!bg-gray-900 dark:!border-gray-700"
            nodeColor={(node) => (node.data as { color?: string }).color || "#999"}
          />
          <Panel position="top-right">
            <ConfigPanel />
          </Panel>
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
};

export default PipelineBuilder;
