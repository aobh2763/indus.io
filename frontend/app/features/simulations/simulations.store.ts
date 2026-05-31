import { create } from "zustand";

const HEARTBEAT_PERIOD = 1000;

export type Heartbeat = {
  simulationId: string;
  intervalId: NodeJS.Timeout;
}

function heartbeatFn(simulationId: string) {
  console.log(simulationId);
}

export type SimulationStoreState = {
  heartbeats: Heartbeat[];
  inspectedSimulationId: string | null;
}

export type SimulationStoreActions = {
  stopSimulation: (simulationId: string) => void;
  startSimulation: (simulationId: string) => void;

  setInspectedSimulationId: (simulationId: string | null) => void;
}

export type SimulationStore = SimulationStoreState & SimulationStoreActions;

export const useSimulationStore = create<SimulationStore>()((set, get) => ({
  heartbeats: [],
  inspectedSimulationId: null,

  startSimulation: (simulationId: string) => {
    const oldHeartbeats = get().heartbeats;
    const count = oldHeartbeats.filter(h => h.simulationId === simulationId).length;

    if (count > 0) {
      return;
    }

    const newHearbeat: Heartbeat = {
      simulationId,
      intervalId: setInterval(() => heartbeatFn(simulationId), HEARTBEAT_PERIOD),
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
