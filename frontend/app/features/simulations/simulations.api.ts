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
  simulationStepSchema,
  type SimulationStep,
} from './simulations.schema';
import z from 'zod';

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

  getSteps: async (id: string): Promise<SimulationStep[]> => {
    const res = await api.get(API_PREFIX + '/simulations/' + id + '/steps');
    return z.array(simulationStepSchema).parse(res.data);
  },
};
