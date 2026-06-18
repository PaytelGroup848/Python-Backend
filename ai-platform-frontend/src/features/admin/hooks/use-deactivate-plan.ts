import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deactivatePlan,
} from "../services/plan-service";

export function useDeactivatePlan() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn:
      deactivatePlan,

    onSuccess: () => {

      queryClient
        .invalidateQueries({

          queryKey: [
            "admin-plans"
          ],
        });
    },
  });
}