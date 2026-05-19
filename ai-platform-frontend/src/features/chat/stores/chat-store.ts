import { create } from "zustand";

import {
  ChatMessage,
} from "../types/chat.types";

interface ChatState {

  messages: ChatMessage[];

  setMessages: (
    messages: ChatMessage[]
  ) => void;

  addMessage: (
    message: ChatMessage
  ) => void;

  updateLastMessage: (
    chunk: string
  ) => void;

  clearMessages: () => void;
}

export const useChatStore =
  create<ChatState>((set) => ({

    messages: [],

    setMessages: (
      messages
    ) =>
      set({
        messages,
     }),

    addMessage: (
      message
    ) =>
      set((state) => ({
        messages: [
          ...state.messages,
          message,
        ],
      })),

    updateLastMessage: (
      chunk
    ) =>
      set((state) => {

        const messages = [
          ...state.messages,
        ];

        const lastMessage =
          [...messages]
            .reverse()
            .find(
              (message) =>
                message.role ===
                "assistant"
          );

        if (
          lastMessage &&
          lastMessage.role ===
          "assistant"
        ) {
          lastMessage.content +=
            chunk;
        }

        return { messages };
      }),

    clearMessages: () =>
      set({
        messages: [],
      }),
  }));