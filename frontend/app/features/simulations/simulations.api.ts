import api, { API_PREFIX } from '~/lib/api';

import {
  createSimulationRequestSchema,
  updateSimulationRequestSchema,
  simulationResponseSchema,
  simulationListResponseSchema,
  type CreateSimulationRequest,
  type UpdateSimulationRequest,
  type SimulationResponse,
  type SimulationListResponse,
} from './simulations.schema';

export const simulationsApi = {
  get: async (line_id: string): Promise<SimulationListResponse> => {
    const res = await api.get(API_PREFIX + '/lines/' + line_id + '/simulations');
    return simulationListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<SimulationResponse> => {
    const res = await api.get(API_PREFIX + '/simulations/' + id);
    return simulationResponseSchema.parse(res.data);
  },

  create: async (
    line_id: string,
    data: CreateSimulationRequest
  ): Promise<SimulationResponse> => {
    createSimulationRequestSchema.parse(data);

    const res = await api.post(
      API_PREFIX + '/lines/' + line_id + '/simulations',
      data
    );

    return simulationResponseSchema.parse(res.data);
  },

  update: async (
    id: string,
    data: UpdateSimulationRequest
  ): Promise<SimulationResponse> => {
    updateSimulationRequestSchema.parse(data);

    const res = await api.put(
      API_PREFIX + '/simulations/' + id,
      data
    );

    return simulationResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/simulations/' + id);
  },

  step: async (id: string): Promise<void> => {
    await api.post(API_PREFIX + '/simulations/' + id + '/step');
  },

  getSteps: async (id: string): Promise<void> => {
    await api.post(API_PREFIX + '/simulations/' + id + '/step');
  },

  explain: async (warning: string): Promise<string> => {
    const res = await api.get(API_PREFIX + '/ai-agents/explain', {
      params: { warning },
    });
    return res.data;
  }
};
