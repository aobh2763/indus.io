import api, { API_PREFIX } from '~/lib/api';

import {
  createMachineRequestSchema,
  updateMachineRequestSchema,
  machineResponseSchema,
  machineListResponseSchema,
  type CreateMachineRequest,
  type UpdateMachineRequest,
  type MachineResponse,
  type MachineListResponse,
} from './machines.schema';

export const machinesApi = {
  get: async (line_id: string): Promise<MachineListResponse> => {
    const res = await api.get(API_PREFIX + '/lines/' + line_id + '/machines');
    return machineListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<MachineResponse> => {
    const res = await api.get(API_PREFIX + '/machines/' + id);
    return machineResponseSchema.parse(res.data);
  },

  create: async (line_id: string, data: CreateMachineRequest): Promise<MachineResponse> => {
    createMachineRequestSchema.parse(data);
    const res = await api.post(API_PREFIX + '/lines/' + line_id + '/machines', data);
    return machineResponseSchema.parse(res.data);
  },

  update: async (id: string, data: UpdateMachineRequest): Promise<MachineResponse> => {
    updateMachineRequestSchema.parse(data);
    const res = await api.put(API_PREFIX + '/machines/' + id, data);
    return machineResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/machines/' + id);
  },
};
