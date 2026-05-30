import { z } from 'zod';

export const visibilitySchema = z.enum(['PUBLIC', 'PRIVATE']);
export type Visibility = z.infer<typeof visibilitySchema>;

export const accessLevelSchema = z.enum(['OWNER', 'SUPERVISOR', 'COLLABORATOR', 'VIEWER']);
export type AccessLevel = z.infer<typeof accessLevelSchema>;

export const createProjectRequestSchema = z.object({
  name: z.string().min(1).max(200),
  description: z.string().optional().nullable(),
  visibility: visibilitySchema.default('PRIVATE'),
});
export type CreateProjectRequest = z.infer<typeof createProjectRequestSchema>;

export const updateProjectRequestSchema = createProjectRequestSchema.partial();
export type UpdateProjectRequest = z.infer<typeof updateProjectRequestSchema>;

export const projectResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().nullable().optional(),
  visibility: visibilitySchema,
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
export type ProjectResponse = z.infer<typeof projectResponseSchema>;

export const projectListResponseSchema = z.array(projectResponseSchema);
export type ProjectListResponse = z.infer<typeof projectListResponseSchema>;

export const createProjectAccessRequestSchema = z.object({
  user_id: z.string().uuid(),
  access_level: accessLevelSchema.default('VIEWER'),
  can_clone: z.boolean().default(false),
});
export type CreateProjectAccessRequest = z.infer<typeof createProjectAccessRequestSchema>;

export const updateProjectAccessRequestSchema = z.object({
  access_level: accessLevelSchema.optional(),
  can_clone: z.boolean().optional(),
});
export type UpdateProjectAccessRequest = z.infer<typeof updateProjectAccessRequestSchema>;

export const projectAccessResponseSchema = z.object({
  id: z.string(),
  project_id: z.string(),
  user_id: z.string(),
  access_level: accessLevelSchema,
  can_clone: z.boolean(),
  created_at: z.coerce.date(),
});
export type ProjectAccessResponse = z.infer<typeof projectAccessResponseSchema>;

export const projectAccessListResponseSchema = z.array(projectAccessResponseSchema);
export type ProjectAccessListResponse = z.infer<typeof projectAccessListResponseSchema>;