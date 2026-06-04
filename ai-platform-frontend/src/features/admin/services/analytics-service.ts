import axios from "axios";

import {
  AnalyticsResponse
} from "../types/analytics";

class AnalyticsService {

  async getOverview():
    Promise<AnalyticsResponse> {

    const response =
      await axios.get(

        "http://localhost:8000/analytics/overview"
      );

    return response.data;
  }
}

export const analyticsService =
  new AnalyticsService();