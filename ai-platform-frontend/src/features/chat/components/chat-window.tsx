"use client";

import { v4 as uuid } from "uuid";

import { MessageList }
  from "./message-list";

import { MessageInput }
  from "./message-input";

import {
  useChatStore,
} from "../stores/chat-store";

import { socketClient }
  from "@/services/websocket/socket-client";

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

  function handleSend(
    content: string
  ) {

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

    socketClient.connect(

     `${window.location.protocol === "https:"
      ? "wss"
      : "ws"}://${window.location.hostname}/ws/chat`,

    (event) => {

     const data =
       JSON.parse(event.data);

     if (
       data.type === "chunk"
     ) {

       updateLastMessage(
         data.content
        );
     }
   }
 );

    socketClient.send({
      message: content,
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
      {/* Messages */}

      <div className="flex-1 overflow-y-auto p-6">

        <MessageList
          messages={messages}
        />
      </div>

      {/* Input */}

      <div className="border-t border-white/10 p-4">

        <MessageInput
          onSend={handleSend}
        />
      </div>
    </div>
  );
}