import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updatePrice,
} from "../services/plan-service";

export function useUpdatePrice() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({

      priceId,

      payload,

    }: any) =>

      updatePrice(
        priceId,
        payload
      ),

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: [
          "plan-prices"
        ],
      });
    },
  });
}