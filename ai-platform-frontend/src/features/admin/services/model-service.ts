import axios from "axios";

import {
  ModelsResponse
} from "../types/model";

class ModelService {

  async getModels():
    Promise<ModelsResponse> {

    const response =
      await axios.get(

        "http://localhost:8000/models"
      );

    return response.data;
  }
  async createModel(
    payload: {
        model_name: string;
        provider: string;
        description?: string;
    }
  ) {

    const response =
        await axios.post(

            "http://localhost:8000/models",

            payload
        );

    return response.data;
   }

   async deleteModel(
    modelName: string
   ) {

    const response =
      await axios.delete(

        `http://localhost:8000/models/${modelName}`
      );

    return response.data;
  }

  async updateModel(
    modelName: string,
    payload: any
  ) {

    const response =
      await axios.patch(

        `http://localhost:8000/models/${modelName}`,

        payload
      );

    return response.data;
  }
}

export const modelService =
  new ModelService();