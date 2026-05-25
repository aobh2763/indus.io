import { z } from 'zod';

export const loginRequestSchema = z.object({
  email: z.email(),
  password: z.string().min(1),
});
export type LoginRequest = z.infer<typeof loginRequestSchema>;

export const registerRequestSchema = z.object({
  email: z.email(),
  password: z.string().min(6),
  firstName: z.string().min(1),
  lastName: z.string().min(1),
});
export type RegisterRequest = z.infer<typeof registerRequestSchema>;

export const loginResponseSchema = z.object({
  token: z.string(),
  expiresIn: z.number(),
});
export type LoginResponse = z.infer<typeof loginResponseSchema>;
