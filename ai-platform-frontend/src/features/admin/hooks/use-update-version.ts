import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateVersion,
} from "../services/plan-service";

export function useUpdateVersion() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({

      versionId,

      payload,

    }: {

      versionId: number;

      payload: {

        monthly_token_limit: number;

        monthly_request_limit: number;

        monthly_cost_limit?: number;
      };
    }) =>

      updateVersion(
        versionId,
        payload
      ),

    onSuccess: () => {

      queryClient.invalidateQueries();
    },
  });
}