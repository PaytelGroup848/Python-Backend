"use client";

import {
  useEffect,
  useRef,
} from "react";

import { v4 as uuid }
  from "uuid";

import { MessageList }
  from "./message-list";

import { MessageInput }
  from "./message-input";

import {
  useChatStore,
} from "../stores/chat-store";

import { socketClient }
  from "@/services/websocket/socket-client";

import { useAuthStore }
  from "@/stores/auth-store";  

import {
  useConversationStore,
} from "../stores/conversation-store";

import {
  updateConversationTitle,
} from "../services/conversation-service";

export function ChatWindow() {

  const messages =
    useChatStore(
      (state) => state.messages
    );

  const addMessage =
    useChatStore(
      (state) => state.addMessage
    );

  const updateLastMessage =
    useChatStore(
      (state) =>
        state.updateLastMessage
    );

  const setStreaming =
  useChatStore(
    (state) =>
      state.setStreaming
  );

  const accessToken =
  useAuthStore(
    (state) =>
      state.accessToken
  );

  const activeConversationId =
  useConversationStore(
    (state) =>
      state.activeConversationId
  );

  const conversations =
  useConversationStore(
    (state) =>
      state.conversations
  );

const setConversations =
  useConversationStore(
    (state) =>
      state.setConversations
  );

  const bottomRef =
  useRef<HTMLDivElement>(null);

  useEffect(() => {

  if (!accessToken) {
    return;
  }

  socketClient.connect(

    `${process.env.NEXT_PUBLIC_WS_URL}/ws/chat?token=${accessToken}`,

    (event) => {

      const data =
        JSON.parse(event.data);

      if (
        data.type === "start"
      ) {

        setStreaming(true);
      }

      if (
        data.type === "chunk"
      ) {

        updateLastMessage(
          data.content
        );
      }

      if (
        data.type === "done"
      ) {

        setStreaming(false);
      }
    }
  );

  return () => {

    socketClient.disconnect();
  };

}, [accessToken]);

  useEffect(() => {

  bottomRef.current?.scrollIntoView({
    behavior: "smooth",
  });

}, [messages]);

  async function handleSend(
    content: string
  ) {

    const shouldGenerateTitle =
      messages.length === 0;

    addMessage({
      id: uuid(),
      role: "user",
      content,
    });

    addMessage({
      id: uuid(),
      role: "assistant",
      content: "",
    });

    if (
      shouldGenerateTitle &&
      activeConversationId
    ) {

     const generatedTitle =
       content
         .slice(0, 40)
         .trim();

       await updateConversationTitle(

         activeConversationId,

         generatedTitle
      );

      const updatedConversations =
        conversations.map(
          (conversation) =>

            conversation.id ===
            activeConversationId

              ? {
                  ...conversation,
                  title:
                    generatedTitle,
                }

              : conversation
        );

      setConversations(
        updatedConversations
      );
    }

    socketClient.send({

     message: content,

     conversation_id:
       activeConversationId,
   });
  }

  return (
    <div
      className="
        flex
        h-[80vh]
        flex-col
        rounded-3xl
        border
        border-white/20
        bg-zinc-900
      "
    >
      <div className="flex-1 overflow-y-auto p-6">

        <MessageList
          messages={messages}
        />
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-white/10 p-4">

        <MessageInput
          onSend={handleSend}
        />
      </div>
    </div>
  );
}