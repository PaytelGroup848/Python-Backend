import { useQuery } from "@tanstack/react-query";

import {
  getPlanPrices,
} from "../services/plan-service";

export function usePlanPrices(
  planId: number
) {

  return useQuery({

    queryKey: [
      "plan-prices",
      planId,
    ],

    queryFn: () =>
      getPlanPrices(
        planId
      ),

    enabled:
      !!planId,
  });
}