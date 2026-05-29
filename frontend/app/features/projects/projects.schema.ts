import { z } from 'zod';

export enum ProjectVisibility {
  PRIVATE = "PRIVATE",
  PUBLIC = "PUBLIC",
}

export const createProjectRequestSchema = z.object({
  name: z.string(),
  description: z.string(),
  visibility: z.enum(ProjectVisibility),
});

export type CreateProjectRequest = z.infer<
  typeof createProjectRequestSchema
>;

export const updateProjectRequestSchema =
  createProjectRequestSchema.partial();

export type UpdateProjectRequest = z.infer<
  typeof updateProjectRequestSchema
>;

export const projectResponseSchema =
  createProjectRequestSchema.extend({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    visibility: z.enum(ProjectVisibility),
    created_at: z.coerce.date(),
    updated_at: z.coerce.date(),
  });

export type ProjectResponse = z.infer<
  typeof projectResponseSchema
>;

export const projectListResponseSchema =
  z.array(projectResponseSchema);

export type ProjectListResponse = z.infer<
  typeof projectListResponseSchema
>;
