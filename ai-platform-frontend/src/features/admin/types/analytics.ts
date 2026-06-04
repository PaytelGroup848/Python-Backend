export interface ProviderAnalytics {
  provider: string;
  requests: number;
}

export interface TopModel {
  model_name: string;
  requests: number;
}

export interface TopUser {
  user_id: number;
  requests: number;
}

export interface AnalyticsResponse {

  total_requests: number;

  average_latency_ms: number;

  total_users: number;

  total_models: number;

  total_api_keys: number;

  providers: ProviderAnalytics[];

  top_models: TopModel[];

  top_users: TopUser[];
}