export interface Subscription {

  id: number;

  user_id: number;

  plan_id: number | null;

  plan_version_id: number | null;

  plan_name: string;

  status: string;

  monthly_token_limit: number;

  auto_renew: boolean;

  start_date: string | null;

  end_date: string | null;

  created_at: string;
}

export interface SubscriptionsResponse {

  count: number;

  subscriptions: Subscription[];
}