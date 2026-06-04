import { useEffect } from "react";
import { useState } from "react";

import {
  modelService
} from "../services/model-service";

import {
  Model
} from "../types/model";

export function useModels() {

  const [models, setModels] =
    useState<Model[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    loadModels();

  }, []);

  async function loadModels() {

    try {

      const data =
        await modelService
          .getModels();

      setModels(
        data.models
      );

    } finally {

      setLoading(false);
    }
  }

  return {

    models,

    loading,

    refresh:
      loadModels
  };
}