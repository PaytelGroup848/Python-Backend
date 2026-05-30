import axios from "axios";

export interface WorkerStatus {
  name: string;
  status: string;
  queue_size: number;
}

export interface WorkerResponse {
  workers: WorkerStatus[];
}

class WorkerService {

  async getWorkers(): Promise<WorkerResponse> {

    const response = await axios.get(
      "http://localhost:8000/admin/workers"
    );

    return response.data;
  }
}

export const workerService =
  new WorkerService();