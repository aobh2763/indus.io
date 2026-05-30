import api, { API_PREFIX } from '~/lib/api';

import {
  createProjectRequestSchema,
  updateProjectRequestSchema,
  projectResponseSchema,
  projectListResponseSchema,
  createProjectAccessRequestSchema,
  updateProjectAccessRequestSchema,
  projectAccessResponseSchema,
  projectAccessListResponseSchema,
  type CreateProjectRequest,
  type UpdateProjectRequest,
  type ProjectResponse,
  type ProjectListResponse,
  type CreateProjectAccessRequest,
  type UpdateProjectAccessRequest,
  type ProjectAccessResponse,
  type ProjectAccessListResponse,
} from './project.schema';

export const projectsApi = {
  getAll: async (): Promise<ProjectListResponse> => {
    const res = await api.get(API_PREFIX + '/projects');
    return projectListResponseSchema.parse(res.data);
  },

  getById: async (id: string): Promise<ProjectResponse> => {
    const res = await api.get(API_PREFIX + '/projects/' + id);
    return projectResponseSchema.parse(res.data);
  },

  create: async (data: CreateProjectRequest): Promise<ProjectResponse> => {
    createProjectRequestSchema.parse(data);
    const res = await api.post(API_PREFIX + '/projects', data);
    return projectResponseSchema.parse(res.data);
  },

  update: async (id: string, data: UpdateProjectRequest): Promise<ProjectResponse> => {
    updateProjectRequestSchema.parse(data);
    const res = await api.put(API_PREFIX + '/projects/' + id, data);
    return projectResponseSchema.parse(res.data);
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/projects/' + id);
  },
};

export const projectAccessApi = {
  getList: async (project_id: string): Promise<ProjectAccessListResponse> => {
    const res = await api.get(API_PREFIX + '/projects/' + project_id + '/access');
    return projectAccessListResponseSchema.parse(res.data);
  },

  grant: async (project_id: string, data: CreateProjectAccessRequest): Promise<ProjectAccessResponse> => {
    createProjectAccessRequestSchema.parse(data);
    const res = await api.post(API_PREFIX + '/projects/' + project_id + '/access', data);
    return projectAccessResponseSchema.parse(res.data);
  },

  update: async (access_id: string, data: UpdateProjectAccessRequest): Promise<ProjectAccessResponse> => {
    updateProjectAccessRequestSchema.parse(data);
    const res = await api.put(API_PREFIX + '/projects/access/' + access_id, data);
    return projectAccessResponseSchema.parse(res.data);
  },

  revoke: async (access_id: string): Promise<void> => {
    await api.delete(API_PREFIX + '/projects/access/' + access_id);
  },
};