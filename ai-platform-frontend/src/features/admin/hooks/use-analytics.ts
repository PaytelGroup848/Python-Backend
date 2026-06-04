import { useEffect } from "react";
import { useState } from "react";

import {
  analyticsService
} from "../services/analytics-service";

import {
  AnalyticsResponse
} from "../types/analytics";

export function useAnalytics() {

  const [data, setData] =
    useState<
      AnalyticsResponse | null
    >(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    loadAnalytics();

  }, []);

  async function loadAnalytics() {

    try {

      const response =
        await analyticsService
          .getOverview();

      setData(response);

    } finally {

      setLoading(false);
    }
  }

  return {

    data,

    loading,

    refresh:
      loadAnalytics
  };
}