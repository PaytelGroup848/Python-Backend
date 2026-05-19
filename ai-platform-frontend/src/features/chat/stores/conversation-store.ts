import { create }
  from "zustand";

import {
  Conversation,
} from "../types/conversation.types";

interface ConversationState {

  conversations:
    Conversation[];

  activeConversationId:
    number | null;

  setConversations: (
    conversations:
      Conversation[]
  ) => void;

  setActiveConversation: (
    id: number
  ) => void;
}

export const
useConversationStore =
  create<ConversationState>(
    (set) => ({

      conversations: [],

      activeConversationId:
        null,

      setConversations: (
        conversations
      ) =>
        set({
          conversations,
        }),

      setActiveConversation: (
        id
      ) =>
        set({
          activeConversationId:
            id,
        }),
    })
  );