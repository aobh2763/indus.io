import { toast } from "sonner";
import { create } from "zustand";
import { machinesApi } from "~/features/machines/machines.api";
import { connectionsApi } from "~/features/connections/connections.api";
import type { AttributeInstance, MachineProcess, MachineTypeConfig, ProcessAttributes } from "./pipeline.schema";
import { getColorForProcess, getIconForProcess } from "./pipeline.schema";
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
import { persist } from "zustand/middleware";

export interface MachineNodeData extends Record<string, unknown> {
  icon: string;
  color: string;
  label: string;
  process: MachineProcess;
  subprocess: string;
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

  lineId: string | null;
  isLoading: boolean;
  isReadOnly: boolean;

  setLineId: (lineId: string) => void;
  setReadOnly: (isReadOnly: boolean) => void;
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

function emptyAttributes(): ProcessAttributes {
  return {
    inputs: {},
    configs: {},
    outputs: {},
  };
}

function inferAttributeType(value: unknown): AttributeInstance["definition"]["type"] {
  if (typeof value === "number") return "number";
  if (typeof value === "boolean") return "boolean";
  return "string";
}

function titleFromKey(key: string) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeAttributeMap(value: unknown): Record<string, AttributeInstance> {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};

  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>).map(([key, raw]) => {
      if (
        raw &&
        typeof raw === "object" &&
        "definition" in raw &&
        "value" in raw &&
        (raw as AttributeInstance).definition
      ) {
        return [key, raw as AttributeInstance];
      }

      return [
        key,
        {
          definition: {
            id: key,
            name: titleFromKey(key),
            type: inferAttributeType(raw),
          },
          value: raw,
        },
      ];
    })
  );
}

function normalizeProcessAttributes(parameters: unknown): ProcessAttributes {
  if (!parameters || typeof parameters !== "object" || Array.isArray(parameters)) {
    return emptyAttributes();
  }

  const maybeGrouped = parameters as Record<string, unknown>;

  const hasBackendShape =
    "machine_parameters" in maybeGrouped ||
    "input_attributes" in maybeGrouped ||
    "output_attributes" in maybeGrouped;

  if (hasBackendShape) {
    return {
      inputs: normalizeAttributeMap(maybeGrouped.input_attributes),
      configs: normalizeAttributeMap(maybeGrouped.machine_parameters),
      outputs: normalizeAttributeMap(maybeGrouped.output_attributes),
    };
  }

  const hasGroupedShape =
    "inputs" in maybeGrouped ||
    "configs" in maybeGrouped ||
    "outputs" in maybeGrouped;

  if (hasGroupedShape) {
    return {
      inputs: normalizeAttributeMap(maybeGrouped.inputs),
      configs: normalizeAttributeMap(maybeGrouped.configs),
      outputs: normalizeAttributeMap(maybeGrouped.outputs),
    };
  }

  return {
    inputs: {},
    configs: normalizeAttributeMap(parameters),
    outputs: {},
  };
}

/** Convert a backend MachineResponse into a ReactFlow MachineNode */
function machineToNode(machine: MachineResponse): MachineNode {
  return {
    id: machine.id,
    type: "machineNode",
    position: { x: machine.position_x ?? 0, y: machine.position_y ?? 0 },
    data: {
      label: machine.name,
      process: (machine.process ?? "spinning") as MachineProcess,
      subprocess: (machine.subprocess ?? "rotor") as MachineProcess,
      color: getColorForProcess(machine.process ?? ""),
      icon: machine.icon ?? getIconForProcess(machine.process ?? ""),
      attributes: normalizeProcessAttributes(machine.parameters),
    },
  };
}

/** Format frontend attributes to the structure expected by the backend */
function formatAttributesForBackend(attributes: ProcessAttributes): Record<string, unknown> {
  const machine_parameters: Record<string, unknown> = {};
  const input_attributes: Record<string, unknown> = {};
  const output_attributes: Record<string, unknown> = {};

  if (attributes.configs) {
    for (const [key, attr] of Object.entries(attributes.configs)) {
      machine_parameters[key] = attr.value;
    }
  }

  if (attributes.inputs) {
    for (const [key, attr] of Object.entries(attributes.inputs)) {
      input_attributes[key] = attr.value;
    }
  }

  if (attributes.outputs) {
    for (const [key, attr] of Object.entries(attributes.outputs)) {
      output_attributes[key] = attr.value;
    }
  }

  return {
    machine_parameters,
    input_attributes,
    output_attributes,
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
  const req = {
    name: data.label,
    process: data.process,
    subprocess: data.subprocess,
    icon: data.icon,
    position_x: position.x,
    position_y: position.y,
    is_configured: false,
    parameters: formatAttributesForBackend(data.attributes),
  };

  console.log("NODE REQUEST:", req);
  return req;
}

// Track debounce timers for position updates per node
const positionTimers: Record<string, ReturnType<typeof setTimeout>> = {};

// ── Store ───────────────────────────────────────────────

export const usePipelineStore = create<PipelineState>()(
  persist(
    (set, get) => ({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      isConfigPanelOpen: false,
      isSimulationPanelOpen: false,
      isMachineLibraryOpen: false,
      dragNDropPosition: null,
      dragNDropMachineName: null,

      lineId: null,
      isLoading: false,
      isReadOnly: false,

      setLineId: (lineId) => set({ lineId }),
      setReadOnly: (isReadOnly) => set({ isReadOnly }),

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
        if (get().isReadOnly) return;

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
        if (get().isReadOnly) return;

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
        if (get().isReadOnly) {
          toast.error("You can view this pipeline, but you cannot modify it");
          return;
        }

        const { lineId } = get();
        if (!lineId) return;

        const tempId = `e-${connection.source}-${connection.target}-${Date.now()}`;

        // ── Enforce 1-in / 1-out constraint ──────────────────────────────
        // Find edges that would violate the rule after this new connection.
        const displaced = get().edges.filter(
          (e) =>
            e.source === connection.source ||   // source already has an outgoing edge
            e.target === connection.target       // target already has an incoming edge
        );

        // Delete displaced edges from the backend before we overwrite local state.
        for (const edge of displaced) {
          connectionsApi.delete(edge.id).catch((err) => {
            console.error("Failed to delete displaced connection:", err);
          });
        }
        // ─────────────────────────────────────────────────────────────────

        // Optimistic: remove displaced edges and add the new one.
        const displacedIds = new Set(displaced.map((e) => e.id));
        set({
          edges: addEdge(
            { ...connection, id: tempId, animated: true },
            get().edges.filter((e) => !displacedIds.has(e.id))
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
        if (get().isReadOnly) {
          toast.error("You can view this pipeline, but you cannot modify it");
          return;
        }

        const { lineId } = get();
        if (!lineId) return;

        const tempId = `machine-${Date.now()}`;

        const newNode: MachineNode = {
          id: tempId,
          type: "machineNode",
          position,
          data: {
            label: machineConfig.name,
            process: machineConfig.process,
            subprocess: machineConfig.subprocess,
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
        if (get().isReadOnly) {
          toast.error("You can view this pipeline, but you cannot modify it");
          return;
        }

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
          updatePayload.parameters = formatAttributesForBackend(data.attributes);
        }

        if (Object.keys(updatePayload).length > 0) {
          machinesApi.update(nodeId, updatePayload).catch((err) => {
            console.error("Failed to update machine:", err);
            toast.error("Failed to update machine");
          });
        }
      },

      removeNode: (nodeId) => {
        if (get().isReadOnly) {
          toast.error("You can view this pipeline, but you cannot modify it");
          return;
        }

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
    }),
    {
      name: 'pipeline-store',
      partialize: (state) => ({ lineId: state.lineId }),
    }
  ),
);
