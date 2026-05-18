import axios from "axios";

import { useAuthStore } from "@/stores/auth-store";

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,

  headers: {
    "Content-Type": "application/json",
  },
});

/* =========================
   REQUEST INTERCEPTOR
========================= */

apiClient.interceptors.request.use(
  (config) => {

    const token =
      useAuthStore
        .getState()
        .accessToken;

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(

  (response) => response,

  async (error) => {

    const originalRequest =
      error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {

      originalRequest._retry = true;

      try {

        const refreshToken =
          useAuthStore
            .getState()
            .refreshToken;

        if (!refreshToken) {
          throw new Error();
        }

        const response =
          await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
            {
              refresh_token:
                refreshToken,
            }
          );

        const newAccessToken =
          response.data.access_token;

        const currentUser =
          useAuthStore
            .getState()
            .user;

        if (currentUser) {

          useAuthStore
            .getState()
            .setAuth(
              currentUser,
              newAccessToken,
              refreshToken
            );
        }

        originalRequest.headers = {
         ...originalRequest.headers,
         Authorization:
           `Bearer ${newAccessToken}`,
        };

        return apiClient(
          originalRequest
        );

      } catch {

        useAuthStore
          .getState()
          .logout();

        window.location.href =
          "/login";
      }
    }

    return Promise.reject(error);
  }
);