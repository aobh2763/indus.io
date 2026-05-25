import { create } from 'zustand';
import { authApi } from './auth.api';
import { persist } from 'zustand/middleware';
import type { UserResponse } from '../users/users.schema';
import type { LoginRequest, RegisterRequest } from './auth.schema';

type AuthState = {
  token: string | null;
  user: UserResponse | null;

  isLoading: boolean;
  isHydrated: boolean;
  isAuthenticated: boolean;

  login: (credentials: LoginRequest) => Promise<void>;
  register: (credentials: RegisterRequest) => Promise<void>;
  logout: () => void;

  hydrateUser: () => Promise<void>;
  setIsHydrated: (isHydrated: boolean) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      isHydrated: false,
      isAuthenticated: false,

      login: async (credentials) => {
        set({ isLoading: true });

        try {
          const { token } = await authApi.login(credentials);

          set({ token });
          await get().hydrateUser();
        } catch (err) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });

          throw err;
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (credentials) => {
        set({ isLoading: true });

        try {
          await authApi.register(credentials);
        } finally {
          set({ isLoading: false });
        }
      },

      hydrateUser: async () => {
        set({ isLoading: true });

        try {
          const user = await authApi.me();

          set({
            user,
            isAuthenticated: true,
          });
        } catch (err) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });

          throw err;
        } finally {
          set({ isLoading: false });
        }
      },

      setIsHydrated: (isHydrated) => {
        set({ isHydrated });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
      onRehydrateStorage: () => async (state) => {
        if (state?.token) {
          await state.hydrateUser();
        }

        state?.setIsHydrated(true);
      },
    }
  )
);
