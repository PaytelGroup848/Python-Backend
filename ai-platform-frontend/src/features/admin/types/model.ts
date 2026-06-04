export interface Model {
  id: number;
  model_name: string;
  provider: string;
  description?: string;
  is_active: boolean;
}

export interface ModelsResponse {
  models: Model[];
}