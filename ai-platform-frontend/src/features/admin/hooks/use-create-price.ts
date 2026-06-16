import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createPrice,
} from "../services/plan-service";

export function useCreatePrice() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({

      planId,

      payload,

    }: {

      planId: number;

      payload: {

        provider: string;

        currency: string;

        amount: number;

        billing_cycle: string;

        external_price_id?: string;
      };
    }) =>

      createPrice(
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