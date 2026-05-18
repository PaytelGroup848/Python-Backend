import { apiClient } from "@/services/api/client";

import {
  LoginPayload,
  SignupPayload,
  AuthResponse,
} from "../types/auth.types";

export const authService = {

  async signup(
    payload: SignupPayload
  ) {
    const response = await apiClient.post<AuthResponse>(
      "/auth/signup",
      payload
    );

    return response.data;
  },

  async login(
    payload: LoginPayload
  ) {
    const response = await apiClient.post<AuthResponse>(
      "/auth/login",
      payload
    );

    return response.data;
  },

  async logout() {
    const response = await apiClient.post(
      "/auth/logout"
    );

    return response.data;
  },
};