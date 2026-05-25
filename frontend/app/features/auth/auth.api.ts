import {
  loginRequestSchema,
  loginResponseSchema,
  registerRequestSchema,
  type LoginRequest,
  type RegisterRequest,
  type LoginResponse
} from './auth.schema';
import api, { API_PREFIX } from '~/lib/api';
import { userResponseSchema, type UserResponse } from '../users/users.schema';

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    loginRequestSchema.parse(data);
    const body = new URLSearchParams(data);
    const res = await api.post(API_PREFIX + '/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    console.log(res.data);
    return loginResponseSchema.parse(res.data);
  },

  register: async (data: RegisterRequest): Promise<void> => {
    registerRequestSchema.parse(data);
    await api.post(API_PREFIX + '/auth/register', data);
  },

  me: async (): Promise<UserResponse> => {
    const res = await api.get(API_PREFIX + '/users/me');
    return userResponseSchema.parse(res.data);
  },
}
