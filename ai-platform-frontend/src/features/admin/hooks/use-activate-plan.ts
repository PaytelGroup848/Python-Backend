import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  activatePlan,
} from "../services/plan-service";

export function useActivatePlan() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn:
      activatePlan,

    onSuccess: () => {

      queryClient.invalidateQueries({

        queryKey: [
          "admin-plans"
        ],
      });
    },
  });
}