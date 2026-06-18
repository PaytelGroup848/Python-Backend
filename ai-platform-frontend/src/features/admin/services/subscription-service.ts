import { apiClient } from "@/services/api/client";

import {
  SubscriptionsResponse,
} from "../types/subscription";

export async function getSubscriptions() {

  const { data } =
    await apiClient.get<SubscriptionsResponse>(
      "/admin/subscriptions"
    );

  return data;
}

export async function activateSubscription(
  subscriptionId: number
) {

  const { data } =
    await apiClient.patch(
      `/admin/subscriptions/${subscriptionId}/activate`
    );

  return data;
}

export async function cancelSubscription(
  subscriptionId: number
) {

  const { data } =
    await apiClient.patch(
      `/admin/subscriptions/${subscriptionId}/cancel`
    );

  return data;
}