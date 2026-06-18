import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  cancelSubscription,
} from "../services/subscription-service";

export function useCancelSubscription() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: (
      subscriptionId: number
    ) =>
      cancelSubscription(
        subscriptionId
      ),

    onSuccess: () => {

      queryClient
        .invalidateQueries({

          queryKey: [
            "admin-subscriptions"
          ],
        });
    },
  });
}