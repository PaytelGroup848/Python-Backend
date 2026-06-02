// src/features/admin/services/user-service.ts

import { apiClient } from "@/services/api/client";

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface UsersResponse {
  users: User[];
}

export async function getUsers(): Promise<UsersResponse> {

  const { data } =
    await apiClient.get<UsersResponse>(
      "/admin/users"
    );

  return data;
}