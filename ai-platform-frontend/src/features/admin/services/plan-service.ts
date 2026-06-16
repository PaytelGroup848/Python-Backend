import { apiClient } from "@/services/api/client";

import {
  PlansResponse,
} from "../types/plan";

export async function getPlans() {

  const { data } =
    await apiClient.get<PlansResponse>(
      "/admin/plans"
    );

  return data;
}

export async function getPlanVersions(
  planId: number
) {

  const { data } =
    await apiClient.get(
      `/admin/plans/${planId}/versions`
    );

  return data;
}

export async function getPlanPrices(
  planId: number
) {

  const { data } =
    await apiClient.get(
      `/admin/plans/${planId}/prices`
    );

  return data;
}

export async function createPlan(
  payload: {

    plan_code: string;

    plan_name: string;

    description?: string;

    is_public: boolean;
  }
) {

  const { data } =
    await apiClient.post(

      "/admin/plans",

      payload
    );

  return data;
}

export async function createVersion(
  planId: number,

  payload: {

    version_number: number;

    monthly_token_limit: number;

    monthly_request_limit: number;

    monthly_cost_limit?: number;
  }
) {

  const { data } =
    await apiClient.post(

      `/admin/plans/${planId}/versions`,

      payload
    );

  return data;
}

export async function createPrice(
  planId: number,

  payload: {

    provider: string;

    currency: string;

    amount: number;

    billing_cycle: string;

    external_price_id?: string;
  }
) {

  const { data } =
    await apiClient.post(

      `/admin/plans/${planId}/prices`,

      payload
    );

  return data;
}

export async function updateVersion(

  versionId: number,

  payload: {

    monthly_token_limit: number;

    monthly_request_limit: number;

    monthly_cost_limit?: number;
  }
) {

  const { data } =
    await apiClient.put(

      `/admin/plans/versions/${versionId}`,

      payload
    );

  return data;
}