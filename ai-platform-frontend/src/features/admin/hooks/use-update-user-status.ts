"use client";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateUserStatus,
} from "../services/user-service";

export function useUpdateUserStatus() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({
      userId,
      isActive,
    }: {
      userId: number;
      isActive: boolean;
    }) =>
      updateUserStatus(
        userId,
        isActive
      ),

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["admin-users"],
      });
    },
  });
}