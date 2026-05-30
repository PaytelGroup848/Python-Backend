import { useQuery } from "@tanstack/react-query";

import {
  queueService,
} from "../services/queue-service";

export function useQueues() {

  return useQuery({

    queryKey: [
      "admin-queues"
    ],

    queryFn: () =>
      queueService.getQueues(),
  });
}