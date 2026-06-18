import { useQuery } from "@tanstack/react-query";

import {
  getSubscriptions,
} from "../services/subscription-service";

export function useSubscriptions() {

  return useQuery({

    queryKey: [
      "admin-subscriptions"
    ],

    queryFn:
      getSubscriptions,
  });
}