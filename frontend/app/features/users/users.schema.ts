import { z } from 'zod';

export const userResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  name: z.string(),
  role: z.string(),
  created_at: z.coerce.date(),
  updated_at: z.coerce.date(),
});

export type UserResponse = z.infer<typeof userResponseSchema>;
