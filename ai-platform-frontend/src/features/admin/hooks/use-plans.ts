import { useQuery } from "@tanstack/react-query";

import {
  getPlans,
} from "../services/plan-service";

export function usePlans() {

  return useQuery({

    queryKey: ["admin-plans"],

    queryFn: getPlans,
  });
}