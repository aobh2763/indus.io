import { z } from 'zod';

export const visibilitySchema = z.enum(['PUBLIC', 'PRIVATE']);
export type Visibility = z.infer<typeof visibilitySchema>;

export const accessLevelSchema = z.enum(['OWNER', 'SUPERVISOR', 'COLLABORATOR', 'VIEWER']);
export type AccessLevel = z.infer<typeof accessLevelSchema>;

export const accessStatusSchema = z.enum(['PENDING', 'ACCEPTED', 'DECLINED']);
export type AccessStatus = z.infer<typeof accessStatusSchema>;

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
  current_user_access_level: accessLevelSchema.nullable().optional(),
  current_user_can_clone: z.boolean().default(false),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
export type ProjectResponse = z.infer<typeof projectResponseSchema>;

export const projectListResponseSchema = z.array(projectResponseSchema);
export type ProjectListResponse = z.infer<typeof projectListResponseSchema>;

export const createProjectAccessRequestSchema = z.object({
  user_id: z.string().uuid().optional(),
  email: z.string().email().optional(),
  access_level: accessLevelSchema.default('VIEWER'),
  can_clone: z.boolean().default(false),
}).refine((value) => Boolean(value.user_id || value.email), {
  message: 'Provide a user ID or email address',
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
  project_name: z.string().nullable().optional(),
  user_id: z.string(),
  invited_by_user_id: z.string().nullable().optional(),
  user_name: z.string().nullable().optional(),
  user_email: z.string().nullable().optional(),
  access_level: accessLevelSchema,
  can_clone: z.boolean(),
  status: accessStatusSchema.default('ACCEPTED'),
  accepted_at: z.coerce.date().nullable().optional(),
  created_at: z.coerce.date(),
});
export type ProjectAccessResponse = z.infer<typeof projectAccessResponseSchema>;

export const projectAccessListResponseSchema = z.array(projectAccessResponseSchema);
export type ProjectAccessListResponse = z.infer<typeof projectAccessListResponseSchema>;

export const projectNotificationResponseSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  actor_user_id: z.string().nullable().optional(),
  project_id: z.string().nullable().optional(),
  access_id: z.string().nullable().optional(),
  type: z.string(),
  title: z.string(),
  message: z.string(),
  read_at: z.coerce.date().nullable().optional(),
  created_at: z.coerce.date(),
});
export type ProjectNotificationResponse = z.infer<typeof projectNotificationResponseSchema>;

export const projectNotificationListResponseSchema = z.array(projectNotificationResponseSchema);
export type ProjectNotificationListResponse = z.infer<typeof projectNotificationListResponseSchema>;
