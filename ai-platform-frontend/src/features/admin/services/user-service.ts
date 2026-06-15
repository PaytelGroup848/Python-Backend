

import { apiClient } from "@/services/api/client";

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;

  plan_name: string;

  monthly_token_limit?: number;

  total_tokens: number;

  remaining_tokens: number;

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

export async function updateUserStatus(
  userId: number,
  isActive: boolean
) {

  const { data } =
    await apiClient.patch(

      `/admin/users/${userId}/status`,

      {
        is_active: isActive,
      }
    );

  return data;
}

export async function updateUserPlan(
  userId: number,
  planName: string
) {

  const { data } =
    await apiClient.patch(

      `/admin/users/${userId}/plan`,

      {
        plan_name: planName,
      }
    );

  return data;
}