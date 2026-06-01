import { z } from 'zod';

export const createMachineRequestSchema = z.object({
  icon: z.string().optional().nullable(),
  name: z.string(),
  process: z.string(),
  subprocess: z.string(),
  description: z.string().optional().nullable(),
  manufacturer: z.string().optional().nullable(),
  model_reference: z.string().optional().nullable(),
  year_introduced: z.number().optional().nullable(),
  position_x: z.number().default(0),
  position_y: z.number().default(0),
  is_configured: z.boolean().default(false),
  parameters: z.record(z.string(), z.unknown()).optional(),
});
export type CreateMachineRequest = z.infer<typeof createMachineRequestSchema>;

export const updateMachineRequestSchema = createMachineRequestSchema.partial();
export type UpdateMachineRequest = z.infer<typeof updateMachineRequestSchema>;

export const machineResponseSchema = createMachineRequestSchema.extend({
  id: z.string(),
  production_line_id: z.string(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});
export type MachineResponse = z.infer<typeof machineResponseSchema>;

export const machineListResponseSchema = z.array(machineResponseSchema);
export type MachineListResponse = z.infer<typeof machineListResponseSchema>;
