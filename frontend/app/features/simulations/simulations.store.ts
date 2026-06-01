import { create } from "zustand";
import { simulationsApi } from "./simulations.api";
import { QueryClient } from "@tanstack/react-query";

const HEARTBEAT_PERIOD = 1000;

export type Heartbeat = {
  simulationId: string;
  intervalId: NodeJS.Timeout;
}

async function heartbeatFn(simulationId: string, queryClient: QueryClient) {
  console.log(simulationId);
  await simulationsApi.step(simulationId);
  /*queryClient.invalidateQueries({
    queryKey: [simulationId],
  });*/
}

export type SimulationStoreState = {
  heartbeats: Heartbeat[];
  inspectedSimulationId: string | null;
}

export type SimulationStoreActions = {
  stopSimulation: (simulationId: string) => void;
  startSimulation: (simulationId: string, queryClient: QueryClient) => void;

  setInspectedSimulationId: (simulationId: string | null) => void;
}

export type SimulationStore = SimulationStoreState & SimulationStoreActions;

export const useSimulationStore = create<SimulationStore>()((set, get) => ({
  heartbeats: [],
  inspectedSimulationId: null,

  startSimulation: (simulationId: string, queryClient: QueryClient) => {
    const oldHeartbeats = get().heartbeats;
    const count = oldHeartbeats.filter(h => h.simulationId === simulationId).length;

    if (count > 0) {
      return;
    }

    const newHearbeat: Heartbeat = {
      simulationId,
      intervalId: setInterval(() => heartbeatFn(simulationId, queryClient), HEARTBEAT_PERIOD),
    }

    set((state) => ({
      ...state,
      heartbeats: [...oldHeartbeats, newHearbeat],
    }))
  },

  stopSimulation: (simulationId: string) => {
    const oldHeartbeats = get().heartbeats;

    set((state) => ({
      ...state,
      heartbeats: oldHeartbeats.filter(h => {
        if (h.simulationId === simulationId) {
          clearInterval(h.intervalId);
          return false;
        }

        return true;
      }),
    }))
  },

  setInspectedSimulationId: (id: string | null) => {
    set((state) => ({
      ...state,
      inspectedSimulationId: id,
    }))
  }
}));
