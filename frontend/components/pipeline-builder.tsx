import { type FC, useCallback, useMemo } from "react";
import { ReactFlow, Background, Controls, MiniMap, type OnSelectionChangeFunc, Panel, ReactFlowProvider, BackgroundVariant } from "@xyflow/react";
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
    <div className="h-screen">
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
          proOptions={{ hideAttribution: true }}
          style={{ background: "#000" }}
        >
          <Panel position="center-left">
            <MachineList />
          </Panel>

          <Panel position="center-right">
            <ConfigPanel />
          </Panel>
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
};

export default PipelineBuilder;
