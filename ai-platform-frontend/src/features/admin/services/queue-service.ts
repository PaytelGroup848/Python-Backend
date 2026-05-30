import axios from "axios";

export interface QueueResponse {
  chat_queue: number;
  embedding_queue: number;
  rag_queue: number;
  voice_queue: number;
}

class QueueService {

  async getQueues(): Promise<QueueResponse> {

    const response = await axios.get(
      "http://localhost:8000/admin/queues"
    );

    return response.data;
  }
}

export const queueService =
  new QueueService();