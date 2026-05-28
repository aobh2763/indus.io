import { toast } from "sonner";
import { create } from "zustand";
import { machinesApi } from "~/features/machines/machines.api";
import { connectionsApi } from "~/features/connections/connections.api";
import type { MachineProcess, MachineTypeConfig, ProcessAttributes } from "./pipeline.schema";
import { DEFAULT_LINE_ID, getColorForProcess, getIconForProcess } from "./pipeline.schema";
import type { CreateMachineRequest } from "~/features/machines/machines.schema";
import type { MachineResponse } from "~/features/machines/machines.schema";
import type { ConnectionResponse } from "~/features/connections/connections.schema";
import {
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
  type XYPosition,
  type NodeChange,
} from "@xyflow/react";

export interface MachineNodeData extends Record<string, unknown> {
  icon: string;
  color: string;
  label: string;
  process: MachineProcess;
  attributes: ProcessAttributes;
}

export type MachineNode = Node<MachineNodeData, "machineNode">;

interface PipelineState {
  edges: Edge[];
  nodes: Node<MachineNodeData>[];
  selectedNodeId: string | null;
  isConfigPanelOpen: boolean;
  isSimulationPanelOpen: boolean;
  isMachineLibraryOpen: boolean;
  dragNDropPosition: XYPosition | null;
  dragNDropMachineName: string | null;

  lineId: string;
  isLoading: boolean;

  setLineId: (lineId: string) => void;
  loadPipeline: (lineId: string) => Promise<void>;

  setEdges: (edges: Edge[]) => void;
  setNodes: (nodes: Node<MachineNodeData>[]) => void;

  onEdgesChange: OnEdgesChange;
  onNodesChange: OnNodesChange;

  addNode: (machineConfig: MachineTypeConfig, position: { x: number; y: number }) => void;
  updateNodeData: (nodeId: string, data: Partial<MachineNodeData>) => void;
  removeNode: (nodeId: string) => void;

  getSelectedNode: () => MachineNode | undefined;
  setSelectedNode: (nodeId: string | null) => void;

  getDragNDropPosition: () => XYPosition | null;
  setDragNDropPosition: (position: XYPosition | null) => void;

  setDragNDropMachineName: (machineName: string | null) => void;

  setConfigPanelOpen: (open: boolean) => void;
  setSimulationPanelOpen: (open: boolean) => void;
  setMachineLibraryOpen: (open: boolean) => void;
  onConnect: OnConnect;
}

// ── Helpers ─────────────────────────────────────────────

/** Convert a backend MachineResponse into a ReactFlow MachineNode */
function machineToNode(machine: MachineResponse): MachineNode {
  return {
    id: machine.id,
    type: "machineNode",
    position: { x: machine.position_x ?? 0, y: machine.position_y ?? 0 },
    data: {
      label: machine.name,
      process: (machine.process ?? "spinning") as MachineProcess,
      color: getColorForProcess(machine.process ?? ""),
      icon: machine.icon ?? getIconForProcess(machine.process ?? ""),
      attributes: (machine.parameters as unknown as ProcessAttributes) ?? {
        inputs: {},
        configs: {},
        outputs: {},
      },
    },
  };
}

/** Convert a backend ConnectionResponse into a ReactFlow Edge */
function connectionToEdge(connection: ConnectionResponse): Edge {
  return {
    id: connection.id,
    source: connection.source_machine_id,
    target: connection.target_machine_id,
    animated: true,
  };
}

/** Build a CreateMachineRequest from node data + position */
function nodeToCreateRequest(
  data: MachineNodeData,
  position: { x: number; y: number }
): CreateMachineRequest {
  return {
    name: data.label,
    process: data.process,
    icon: data.icon,
    position_x: position.x,
    position_y: position.y,
    is_configured: false,
    parameters: data.attributes as unknown as Record<string, unknown>,
  };
}

// Track debounce timers for position updates per node
const positionTimers: Record<string, ReturnType<typeof setTimeout>> = {};

// ── Store ───────────────────────────────────────────────

export const usePipelineStore = create<PipelineState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  isConfigPanelOpen: false,
  isSimulationPanelOpen: false,
  isMachineLibraryOpen: false,
  dragNDropPosition: null,
  dragNDropMachineName: null,

  lineId: DEFAULT_LINE_ID,
  isLoading: false,

  setLineId: (lineId) => set({ lineId }),

  loadPipeline: async (lineId) => {
    set({ isLoading: true, lineId });
    try {
      const [machines, connections] = await Promise.all([
        machinesApi.get(lineId),
        connectionsApi.get(lineId),
      ]);

      const nodes = machines.map(machineToNode);
      const edges = connections.map(connectionToEdge);

      set({ nodes, edges, isLoading: false });
    } catch (error) {
      console.error("Failed to load pipeline:", error);
      toast.error("Failed to load pipeline data");
      set({ isLoading: false });
    }
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes) as MachineNode[],
    });

    // Debounce position updates to the backend
    const { lineId } = get();
    for (const change of changes as NodeChange<MachineNode>[]) {
      if (change.type === "position" && change.dragging === false && change.position) {
        const nodeId = change.id;
        const position = change.position;

        // Clear any existing timer for this node
        if (positionTimers[nodeId]) {
          clearTimeout(positionTimers[nodeId]);
        }

        positionTimers[nodeId] = setTimeout(() => {
          machinesApi
            .update(nodeId, {
              position_x: position.x,
              position_y: position.y,
            })
            .catch((err) => {
              console.error("Failed to sync node position:", err);
            });
          delete positionTimers[nodeId];
        }, 500);
      }

      // Handle node removal from keyboard/backspace
      if (change.type === "remove") {
        const nodeId = change.id;
        // Delete the machine from backend
        machinesApi.delete(nodeId).catch((err) => {
          console.error("Failed to delete machine:", err);
          toast.error("Failed to delete machine from server");
        });
        // Delete related connections
        const relatedEdges = get().edges.filter(
          (e) => e.source === nodeId || e.target === nodeId
        );
        for (const edge of relatedEdges) {
          connectionsApi.delete(edge.id).catch((err) => {
            console.error("Failed to delete connection:", err);
          });
        }
      }
    }
  },

  onEdgesChange: (changes) => {
    // Before applying, track edges that are being removed
    for (const change of changes) {
      if (change.type === "remove") {
        const edgeId = change.id;
        connectionsApi.delete(edgeId).catch((err) => {
          console.error("Failed to delete connection:", err);
          toast.error("Failed to delete connection from server");
        });
      }
    }

    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    const { lineId } = get();
    const tempId = `e-${connection.source}-${connection.target}-${Date.now()}`;

    // Optimistic: add edge locally with temp ID
    set({
      edges: addEdge(
        {
          ...connection,
          id: tempId,
          animated: true,
        },
        get().edges
      ),
    });

    // Persist to backend
    connectionsApi
      .create(lineId, {
        source_machine_id: connection.source!,
        target_machine_id: connection.target!,
        weight: 1.0,
      })
      .then((created) => {
        // Replace temp ID with server-assigned ID
        set({
          edges: get().edges.map((edge) =>
            edge.id === tempId ? { ...edge, id: created.id } : edge
          ),
        });
      })
      .catch((err) => {
        console.error("Failed to create connection:", err);
        toast.error("Failed to save connection");
        // Rollback: remove the temp edge
        set({
          edges: get().edges.filter((edge) => edge.id !== tempId),
        });
      });
  },

  addNode: (machineConfig, position) => {
    const { lineId } = get();
    const tempId = `machine-${Date.now()}`;

    const newNode: MachineNode = {
      id: tempId,
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

    // Optimistic: add node locally
    set({ nodes: [...get().nodes, newNode] });

    // Persist to backend
    const request = nodeToCreateRequest(newNode.data, position);
    machinesApi
      .create(lineId, request)
      .then((created) => {
        // Replace temp ID with server-assigned ID
        set({
          nodes: get().nodes.map((node) =>
            node.id === tempId ? { ...node, id: created.id } : node
          ),
        });
      })
      .catch((err) => {
        console.error("Failed to create machine:", err);
        toast.error("Failed to save machine");
        // Rollback: remove the temp node
        set({
          nodes: get().nodes.filter((node) => node.id !== tempId),
        });
      });
  },

  updateNodeData: (nodeId, data) => {
    // Optimistic: update locally
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...data } } : node
      ),
    });

    // Persist to backend
    const updatePayload: Record<string, unknown> = {};
    if (data.label !== undefined) updatePayload.name = data.label;
    if (data.process !== undefined) updatePayload.process = data.process;
    if (data.icon !== undefined) updatePayload.icon = data.icon;
    if (data.attributes !== undefined) {
      updatePayload.parameters = data.attributes;
    }

    if (Object.keys(updatePayload).length > 0) {
      machinesApi.update(nodeId, updatePayload).catch((err) => {
        console.error("Failed to update machine:", err);
        toast.error("Failed to update machine");
      });
    }
  },

  removeNode: (nodeId) => {
    // Capture edges to delete before removing from state
    const edgesToDelete = get().edges.filter(
      (edge) => edge.source === nodeId || edge.target === nodeId
    );

    // Optimistic: remove locally
    set({
      nodes: get().nodes.filter((node) => node.id !== nodeId),
      edges: get().edges.filter((edge) => edge.source !== nodeId && edge.target !== nodeId),
      selectedNodeId: get().selectedNodeId === nodeId ? null : get().selectedNodeId,
      isConfigPanelOpen: get().selectedNodeId === nodeId ? false : get().isConfigPanelOpen,
      isSimulationPanelOpen: false,
    });

    // Persist to backend — delete connections first, then machine
    Promise.all(
      edgesToDelete.map((edge) =>
        connectionsApi.delete(edge.id).catch((err) => {
          console.error("Failed to delete connection:", err);
        })
      )
    ).then(() => {
      machinesApi.delete(nodeId).catch((err) => {
        console.error("Failed to delete machine:", err);
        toast.error("Failed to delete machine from server");
      });
    });
  },

  setSelectedNode: (nodeId) => {
    set({
      selectedNodeId: nodeId,
      isConfigPanelOpen: nodeId !== null,
      isSimulationPanelOpen: false,
    });
  },

  getSelectedNode: () => {
    const { nodes, selectedNodeId } = get();
    return nodes.find((node) => node.id === selectedNodeId) as MachineNode | undefined;
  },

  setDragNDropMachineName: (machineName) => {
    set({ dragNDropMachineName: machineName });
  },

  setDragNDropPosition: (position) => {
    set({ dragNDropPosition: position });
  },

  getDragNDropPosition: () => {
    return get().dragNDropPosition;
  },

  setConfigPanelOpen: (open) => {
    set({
      isConfigPanelOpen: open,
      isSimulationPanelOpen: false,
      selectedNodeId: open ? get().selectedNodeId : null,
    });
  },

  setSimulationPanelOpen: (open) => {
    set({
      isConfigPanelOpen: false,
      isSimulationPanelOpen: open,
      selectedNodeId: null,
    });
  },

  setMachineLibraryOpen: (open) => {
    set({
      isMachineLibraryOpen: open,
    });
  },
}));
