import { apiClient }
  from "@/services/api/client";

import {
  Conversation,
} from "../types/conversation.types";


export async function
createConversation() {

  const response =
    await apiClient.post(
      "/conversations",
      {
        title: "New Chat",
      }
    );

  return response.data;
}


export async function
getConversations():

Promise<Conversation[]> {

  const response =
    await apiClient.get(
      "/conversations"
    );

  return response.data;
}

export async function
getConversationMessages(
  conversationId: number
) {

  const response =
    await apiClient.get(

      `/conversations/${conversationId}/messages`
    );

  return response.data;
}