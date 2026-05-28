import api, { API_PREFIX } from '~/lib/api';

import {
  createConnectionRequestSchema,
  updateConnectionRequestSchema,
  connectionResponseSchema,
  connectionListResponseSchema,
  type CreateConnectionRequest,
  type UpdateConnectionRequest,
  type ConnectionResponse,
  type ConnectionListResponse,
} from './connections.schema';

export const connectionsApi = {
  get: async (line_id: string): Promise<ConnectionListResponse> => {
    const res = await api.get(API_PREFIX + '/lines/' + line_id + '/connections');
    return connectionListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<ConnectionResponse> => {
    const res = await api.get(API_PREFIX + '/connections/' + id);
    return connectionResponseSchema.parse(res.data);
  },

  create: async (line_id: string, data: CreateConnectionRequest): Promise<ConnectionResponse> => {
    createConnectionRequestSchema.parse(data);
    const res = await api.post(API_PREFIX + '/lines/' + line_id + '/connections', data);
    return connectionResponseSchema.parse(res.data);
  },

  update: async (id: string, data: UpdateConnectionRequest): Promise<ConnectionResponse> => {
    updateConnectionRequestSchema.parse(data);
    const res = await api.put(API_PREFIX + '/connections/' + id, data);
    return connectionResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/connections/' + id);
  },
};
