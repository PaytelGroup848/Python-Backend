import { useQuery } from "@tanstack/react-query";

import {
  getPlanVersions,
} from "../services/plan-service";

export function usePlanVersions(
  planId: number
) {

  return useQuery({

    queryKey: [
      "plan-versions",
      planId,
    ],

    queryFn: () =>
      getPlanVersions(
        planId
      ),

    enabled:
      !!planId,
  });
}