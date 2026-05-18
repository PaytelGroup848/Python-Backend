import { create } from "zustand";

import { persist } from "zustand/middleware";

import {
  AuthUser,
} from "@/features/auth/types/auth.types";

interface AuthState {

  user: AuthUser | null;

  accessToken: string | null;

  refreshToken: string | null;

  hydrated: boolean;

  setHydrated: (
    state: boolean
  ) => void;

  setAuth: (
    user: AuthUser,
    accessToken: string,
    refreshToken: string
  ) => void;

  logout: () => void;
}

export const useAuthStore =
  create<AuthState>()(
    persist(
      (set) => ({

        user: null,

        accessToken: null,

        refreshToken: null,

        hydrated: false,

        setHydrated: (
          state
        ) =>
          set({
            hydrated: state,
          }),

        setAuth: (
          user,
          accessToken,
          refreshToken
        ) =>
          set({
            user,
            accessToken,
            refreshToken,
          }),

        logout: () =>
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
          }),
      }),

      {
        name: "ai-platform-auth",

        onRehydrateStorage: () => {

          return (state) => {

            state?.setHydrated(true);
          };
        },
      }
    )
  );