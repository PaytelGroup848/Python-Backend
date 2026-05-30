import axios from "axios";

export interface ProviderStatus {
  name: string;
  status: string;
  latency_ms: number;
}

export interface ProviderResponse {
  providers: ProviderStatus[];
}

class ProviderService {

  async getProviders(): Promise<ProviderResponse> {

    const response = await axios.get(
      "http://localhost:8000/admin/providers"
    );

    return response.data;
  }
}

export const providerService =
  new ProviderService();