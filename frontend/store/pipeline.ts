import { create } from "zustand";
import { applyNodeChanges, applyEdgeChanges, addEdge, type Node, type Edge, type OnNodesChange, type OnEdgesChange, type OnConnect } from "@xyflow/react";
import type { MachineProcess, MachineTypeConfig, ProcessAttributes } from "../types/machine";

export interface MachineNodeData extends Record<string, unknown> {
  label: string;
  process: MachineProcess;
  color: string;
  icon: string;
  attributes: ProcessAttributes;
}

export type MachineNode = Node<MachineNodeData, "machineNode">;

interface PipelineState {
  nodes: Node<MachineNodeData>[];
  edges: Edge[];
  selectedNodeId: string | null;
  isConfigPanelOpen: boolean;

  setNodes: (nodes: Node<MachineNodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNode: (machineConfig: MachineTypeConfig, position: { x: number; y: number }) => void;
  updateNodeData: (nodeId: string, data: Partial<MachineNodeData>) => void;
  removeNode: (nodeId: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setConfigPanelOpen: (open: boolean) => void;
  getSelectedNode: () => MachineNode | undefined;
}

export const usePipelineStore = create<PipelineState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  isConfigPanelOpen: false,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes) as MachineNode[],
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    set({
      edges: addEdge(
        {
          ...connection,
          id: `e-${connection.source}-${connection.target}-${Date.now()}`,
        },
        get().edges
      ),
    });
  },

  addNode: (machineConfig, position) => {
    const newNode: MachineNode = {
      id: `machine-${Date.now()}`,
      type: "machineNode",
      position,
      data: {
        label: machineConfig.name,
        process: machineConfig.process,
        color: machineConfig.color,
        icon: machineConfig.icon,
        attributes: JSON.parse(JSON.stringify(machineConfig.defaultAttributes)),
      },
    };
    set({ nodes: [...get().nodes, newNode] });
  },

  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    });
  },

  removeNode: (nodeId) => {
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
      selectedNodeId: get().selectedNodeId === nodeId ? null : get().selectedNodeId,
      isConfigPanelOpen: get().selectedNodeId === nodeId ? false : get().isConfigPanelOpen,
    });
  },

  setSelectedNode: (nodeId) => {
    set({
      selectedNodeId: nodeId,
      isConfigPanelOpen: nodeId !== null,
    });
  },

  setConfigPanelOpen: (open) => {
    set({
      isConfigPanelOpen: open,
      selectedNodeId: open ? get().selectedNodeId : null,
    });
  },

  getSelectedNode: () => {
    const { nodes, selectedNodeId } = get();
    return nodes.find((node) => node.id === selectedNodeId) as MachineNode | undefined;
  },
}));
