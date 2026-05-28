import { z } from 'zod';

export enum SimulationStatus {
  RUNNING = "RUNNING",
  STOPPED = "STOPPED",
  COMPLETED = "COMPLETED",
}

export const createSimulationRequestSchema = z.object({
  status: z.enum(SimulationStatus),
});
export type CreateSimulationRequest = z.infer<typeof createSimulationRequestSchema>;

export const updateSimulationRequestSchema = createSimulationRequestSchema.partial();
export type UpdateSimulationRequest = z.infer<typeof updateSimulationRequestSchema>;

export const simulationResponseSchema = createSimulationRequestSchema.extend({
  id: z.string(),
  production_line_id: z.string(),
  status: z.enum(SimulationStatus),
  start_time: z.coerce.date(),
  end_time: z.coerce.date(),
});
export type SimulationResponse = z.infer<typeof simulationResponseSchema>;

export const simulationListResponseSchema = z.array(simulationResponseSchema);
export type SimulationListResponse = z.infer<typeof simulationListResponseSchema>;
