import { z } from 'zod';

export const loginRequestSchema = z.object({
  email: z.email(),
  password: z.string().min(1),
});
export type LoginRequest = z.infer<typeof loginRequestSchema>;

export const registerRequestSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
  password: z.string().min(6),
});
export type RegisterRequest = z.infer<typeof registerRequestSchema>;

export const loginResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
});
export type LoginResponse = z.infer<typeof loginResponseSchema>;
