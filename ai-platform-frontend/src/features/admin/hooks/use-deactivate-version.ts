import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deactivateVersion,
} from "../services/plan-service";

export function useDeactivateVersion() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn:
      deactivateVersion,

    onSuccess: () => {

      queryClient.invalidateQueries({

        queryKey: [
          "plan-versions"
        ],
      });
    },
  });
}