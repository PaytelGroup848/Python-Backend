import { create } from "zustand";

import {
  ChatMessage,
} from "../types/chat.types";

interface ChatState {

  messages: ChatMessage[];

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
          messages[
            messages.length - 1
          ];

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