import axios from "axios";

import { DashboardData } from "../types/dashboard";

class DashboardService {

  async getDashboard(): Promise<DashboardData> {

    const response = await axios.get(
      "http://localhost:8000/admin/dashboard"
    );

    return response.data;
  }
}

export const dashboardService =
  new DashboardService();