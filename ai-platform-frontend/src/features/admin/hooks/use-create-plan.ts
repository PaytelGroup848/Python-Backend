import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createPlan,
} from "../services/plan-service";

export function useCreatePlan() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn:
      createPlan,

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