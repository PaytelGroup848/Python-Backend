import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createVersion,
} from "../services/plan-service";

export function useCreateVersion() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({

      planId,

      payload,

    }: {

      planId: number;

      payload: {

        version_number: number;

        monthly_token_limit: number;

        monthly_request_limit: number;

        monthly_cost_limit?: number;
      };
    }) =>

      createVersion(
        planId,
        payload
      ),

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