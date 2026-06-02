"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getUsers,
  UsersResponse,
} from "../services/user-service";

export function useUsers() {

  return useQuery<UsersResponse>({
    queryKey: ["admin-users"],
    queryFn: getUsers,
  });
}