import { z } from 'zod';

export const createConnectionRequestSchema = z.object({
  source_machine_id: z.string(),
  target_machine_id: z.string(),
  weight: z.number(),
});
export type CreateConnectionRequest = z.infer<typeof createConnectionRequestSchema>;

export const updateConnectionRequestSchema = createConnectionRequestSchema.partial();
export type UpdateConnectionRequest = z.infer<typeof updateConnectionRequestSchema>;

export const connectionResponseSchema = createConnectionRequestSchema.extend({
  id: z.string(),
  production_line_id: z.string(),
  created_at: z.coerce.date(),
});
export type ConnectionResponse = z.infer<typeof connectionResponseSchema>;

export const connectionListResponseSchema = z.array(connectionResponseSchema);
export type ConnectionListResponse = z.infer<typeof connectionListResponseSchema>;
