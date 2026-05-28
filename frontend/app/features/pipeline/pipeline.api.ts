import api, { API_PREFIX } from '~/lib/api';

import {
  createProductionLineRequestSchema,
  updateProductionLineRequestSchema,
  productionLineResponseSchema,
  productionLineListResponseSchema,
  type CreateProductionLineRequest,
  type UpdateProductionLineRequest,
  type ProductionLineResponse,
  type ProductionLineListResponse,
} from './pipeline.schema';

export const productionLinesApi = {
  get: async (project_id: string): Promise<ProductionLineListResponse> => {
    const res = await api.get(API_PREFIX + '/projects/' + project_id + '/lines');
    return productionLineListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<ProductionLineResponse> => {
    const res = await api.get(API_PREFIX + '/lines/' + id);
    return productionLineResponseSchema.parse(res.data);
  },

  create: async (
    project_id: string,
    data: CreateProductionLineRequest
  ): Promise<ProductionLineResponse> => {
    createProductionLineRequestSchema.parse(data);

    const res = await api.post(
      API_PREFIX + '/projects/' + project_id + '/lines',
      data
    );

    return productionLineResponseSchema.parse(res.data);
  },

  update: async (
    id: string,
    data: UpdateProductionLineRequest
  ): Promise<ProductionLineResponse> => {
    updateProductionLineRequestSchema.parse(data);

    const res = await api.put(
      API_PREFIX + '/lines/' + id,
      data
    );

    return productionLineResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/lines/' + id);
  },
};
