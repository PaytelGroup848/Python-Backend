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

  console.log(
    "CREATE CONVERSATION RESPONSE:",
    response.data
  );

  return (
    response.data.data
    ||
    response.data
  );
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

export async function
deleteConversation(
  conversationId: number
) {

  const response =
    await apiClient.delete(

      `/conversations/${conversationId}`
    );

  return response.data;
}

export async function
updateConversationTitle(
  conversationId: number,
  title: string
) {

  const response =
    await apiClient.patch(

      `/conversations/${conversationId}/title`,

      {
        title,
      }
    );

  return response.data;
}