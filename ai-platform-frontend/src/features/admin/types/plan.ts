export interface Plan {

  id: number;

  plan_code: string;

  plan_name: string;

  description: string;

  is_public: boolean;

  is_active: boolean;

  created_at: string;

  updated_at: string;
}

export interface PlansResponse {

  count: number;

  plans: Plan[];
}

export interface PlanVersion {

  id: number;

  plan_id: number;

  version_number: number;

  monthly_token_limit: number;

  monthly_request_limit: number;

  monthly_cost_limit: number;

  is_active: boolean;

  created_at: string;
}

export interface PlanVersionsResponse {

  count: number;

  versions: PlanVersion[];
}

export interface PlanPrice {

  id: number;

  plan_version_id: number;

  provider: string;

  external_price_id: string | null;

  currency: string;

  amount: number;

  billing_cycle: string;

  is_active: boolean;
}

export interface PlanPricesResponse {

  count: number;

  prices: PlanPrice[];
}