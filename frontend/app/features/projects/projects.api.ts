import api, { API_PREFIX } from '~/lib/api';

import {
  createProjectRequestSchema,
  updateProjectRequestSchema,
  projectResponseSchema,
  projectListResponseSchema,
  type CreateProjectRequest,
  type UpdateProjectRequest,
  type ProjectResponse,
  type ProjectListResponse,
} from './projects.schema';

export const projectsApi = {
  get: async (): Promise<ProjectListResponse> => {
    const res = await api.get(API_PREFIX + '/projects');
    return projectListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<ProjectResponse> => {
    const res = await api.get(API_PREFIX + '/projects/' + id);
    return projectResponseSchema.parse(res.data);
  },

  create: async (
    data: CreateProjectRequest
  ): Promise<ProjectResponse> => {
    createProjectRequestSchema.parse(data);

    const res = await api.post(
      API_PREFIX + '/projects',
      data
    );

    return projectResponseSchema.parse(res.data);
  },

  update: async (
    id: string,
    data: UpdateProjectRequest
  ): Promise<ProjectResponse> => {
    updateProjectRequestSchema.parse(data);

    const res = await api.put(
      API_PREFIX + '/projects/' + id,
      data
    );

    return projectResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/projects/' + id);
  },
};
