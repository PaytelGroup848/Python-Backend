import { apiClient } from "@/services/api/client";

import {
  PaymentsResponse,
} from "../types/payment";

export async function getPayments() {

  const { data } =
    await apiClient.get<PaymentsResponse>(
      "/admin/payments"
    );

  return data;
}