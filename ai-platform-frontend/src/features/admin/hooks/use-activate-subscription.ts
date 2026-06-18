import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  activateSubscription,
} from "../services/subscription-service";

export function useActivateSubscription() {

  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: (
      subscriptionId: number
    ) =>
      activateSubscription(
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