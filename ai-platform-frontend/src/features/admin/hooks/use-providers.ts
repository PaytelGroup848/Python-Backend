import { useQuery } from "@tanstack/react-query";

import {
  providerService,
} from "../services/provider-service";

export function useProviders() {

  return useQuery({

    queryKey: [
      "admin-providers"
    ],

    queryFn: () =>
      providerService.getProviders(),
  });
}