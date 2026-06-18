import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deactivatePrice,
} from "../services/plan-service";

export function useDeactivatePrice() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn:
      deactivatePrice,

    onSuccess: () => {

      queryClient.invalidateQueries({

        queryKey: [
          "plan-prices"
        ],
      });
    },
  });
}