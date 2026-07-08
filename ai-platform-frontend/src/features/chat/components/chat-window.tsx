

"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import { v4 as uuid }
  from "uuid";

import {
  ArrowUp,
  ChevronDown,
  Mic,
  Plus,
  Sparkles,
} from "lucide-react";

import { MessageList }
  from "./message-list";

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
import { MessageInput } from "./message-input";

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

  const isStreaming =
  useChatStore(
    (state) =>
      state.isStreaming
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

  const [draft, setDraft] =
    useState("");

  useEffect(() => {

  if (!accessToken) {
    return;
  }

  socketClient.connect(

    `${process.env.NEXT_PUBLIC_WS_URL}/ws/chat?token=${accessToken}`,

    (data) => {

      console.log(
        "WS DATA:",
        data
      );

      if (
        data.type === "start"
      ) {

        setStreaming(true);

        addMessage({
          id: uuid(),
          role: "assistant",
          content: "",
        });

        return;
      }

      if (
        data.type === "chunk"
      ) {

        updateLastMessage(
          data.content || ""
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

    if (!content.trim()) {
      return;
    }

    const shouldGenerateTitle =
      messages.length === 0;

    addMessage({
      id: uuid(),
      role: "user",
      content,
    });

    setDraft("");

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
    if (
      socketClient.status !==
      "connected"
    ) {

      alert(
        "WebSocket not connected yet"
      );

      return;
    }


    const currentConversationId =

      useConversationStore
        .getState()
        .activeConversationId;

    console.log(
      "ACTIVE CONVERSATION:",
      currentConversationId
    );

    if (!currentConversationId) {

      alert(
        "Please create/select a conversation first"
      );

      return;
    }

    socketClient.send({

      message: content,

      conversation_id:
        currentConversationId,
    });

  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {

    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend(draft);
    }
  }

  const isEmpty = messages.length === 0;

  const user = useAuthStore(
    (state) => state.user
  );

  {console.log(
    "USER:",
    user
  )}

  function getGreeting() {
  const istHour = Number(
    new Date().toLocaleString("en-US", {
      timeZone: "Asia/Kolkata",
      hour: "2-digit",
      hour12: false,
    })
  );

  if (istHour < 12) return "Good morning";
  if (istHour < 17) return "Good afternoon";
  return "Good evening";
}

  const displayName = getGreeting();

  return (
<div className="relative flex h-[100vh] flex-col overflow-hidden bg-[radial-gradient(120%_60%_at_50%_0%,#93c5fd_0%,#f5f3ff_20%,transparent_45%),radial-gradient(120%_70%_at_10%_100%,#c026d3_0%,transparent_60%),radial-gradient(120%_70%_at_90%_100%,#db2777_0%,transparent_60%)] bg-white shadow-[0_8px_40px_-12px_rgba(147,51,234,0.2)]">
      {/* animated gradient background */}
      <div className="absolute inset-0 -z-10 overflow-hidden bg-white">
        <div className="absolute -top-32 left-1/2 h-[520px] w-[1100px] -translate-x-1/2 rounded-full bg-sky-200/70 blur-[110px]" />
        <div className="absolute top-1/4 -left-40 h-[420px] w-[720px] rounded-full bg-indigo-300/50 blur-[120px]" />
        <div className="absolute bottom-[-160px] left-[-80px] h-[520px] w-[820px] rounded-full bg-fuchsia-400/70 blur-[110px]" />
        <div className="absolute bottom-[-220px] right-[-100px] h-[560px] w-[860px] rounded-full bg-pink-500/80 blur-[110px]" />
        <div className="absolute bottom-[-260px] left-1/2 h-[440px] w-[1000px] -translate-x-1/2 rounded-full bg-rose-500/60 blur-[100px]" />
      </div>

      {isEmpty ? (
        // ---------- Landing / hero state ----------
        <div className="relative z-10 flex h-full flex-col items-center justify-center gap-7 px-6">

        

          <h1 className="max-w-xl text-center text-3xl font-semibold tracking-tight text-zinc-900 sm:text-4xl">
             {displayName}, What&apos;s the vision?
          </h1>

          <MessageInput
          onSend={handleSend}
        />
        </div>
      ) : (
        // ---------- Active conversation state ----------
        <>
          <div className="relative z-10 flex-1 overflow-y-auto px-6 py-6">
            <MessageList messages={messages} />
            <div ref={bottomRef} />
          </div>

          <div className="relative z-10 flex justify-center px-6 pb-6">
            <MessageInput
          onSend={handleSend}
        />
          </div>
        </>
      )}
    </div>
  );
}