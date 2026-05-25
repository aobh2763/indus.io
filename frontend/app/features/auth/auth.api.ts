import {
  loginRequestSchema,
  loginResponseSchema,
  registerRequestSchema,
  type LoginRequest,
  type RegisterRequest,
  type LoginResponse
} from './auth.schema';
import api from '~/lib/api';
import { userResponseSchema, type UserResponse } from '../users/users.schema';

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    loginRequestSchema.parse(data);
    const res = await api.post('/auth/login', data);
    return loginResponseSchema.parse(res.data);
  },

  register: async (data: RegisterRequest): Promise<void> => {
    registerRequestSchema.parse(data);
    await api.post('/auth/register', data);
  },

  me: async (): Promise<UserResponse> => {
    const res = await api.get('/auth/me');
    return userResponseSchema.parse(res.data);
  },
}
