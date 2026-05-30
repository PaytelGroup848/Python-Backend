import { useQuery } from "@tanstack/react-query";

import {
  dashboardService,
} from "../services/dashboard-service";

export function useDashboard() {

  return useQuery({

    queryKey: [
      "admin-dashboard"
    ],

    queryFn: () =>
      dashboardService.getDashboard(),
  });
}