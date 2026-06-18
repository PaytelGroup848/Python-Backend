import {
  useQuery,
} from "@tanstack/react-query";

import {
  getPayments,
} from "../services/payment-service";

export function usePayments() {

  return useQuery({

    queryKey: [
      "admin-payments"
    ],

    queryFn:
      getPayments,
  });
}