"use client";

import {
  useEffect,
} from "react";

import {
  Plus,
} from "lucide-react";

import {
  createConversation,
  getConversations,
  getConversationMessages,
} from "../services/conversation-service";

import {
  useConversationStore,
} from "../stores/conversation-store";

import {
  useChatStore,
} from "../stores/chat-store";


export function
ConversationSidebar() {

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

  const activeConversationId =
    useConversationStore(
      (state) =>
        state.activeConversationId
    );

  const setActiveConversation =
    useConversationStore(
      (state) =>
        state.setActiveConversation
    );

  const setMessages =
  useChatStore(
    (state) =>
      state.setMessages
  );

  /* =========================
     LOAD CONVERSATIONS
  ========================= */

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getConversations();

        setConversations(data);

        if (data.length > 0) {

  const latestConversation =
    data[0];

  setActiveConversation(
    latestConversation.id
  );

  const messages =
    await getConversationMessages(
      latestConversation.id
    );

  setMessages(messages);
}

      } catch (error) {

        console.error(
          error
        );
      }
    }

    load();

  }, []);

  /* =========================
     CREATE CHAT
  ========================= */

  async function handleNewChat() {

  try {

    const conversation =
      await createConversation();

    const updatedConversations =
      await getConversations();

    setConversations(
      updatedConversations
    );

    setActiveConversation(
      conversation.id
    );

    setMessages([]);

  } catch (error) {

    console.error(error);
  }
}

  return (
    <div
      className="
        flex
        h-full
        w-80
        flex-col
        border-r
        border-white/10
        bg-zinc-950
      "
    >
      {/* HEADER */}

      <div className="p-4">

        <button
          onClick={handleNewChat}
          className="
            flex
            w-full
            items-center
            justify-center
            gap-2
            rounded-xl
            bg-white
            px-4
            py-3
            text-sm
            font-medium
            text-black
            transition-all
            hover:scale-[1.02]
          "
        >
          <Plus size={18} />

          New Chat
        </button>
      </div>

      {/* CONVERSATIONS */}

      <div
        className="
          flex-1
          overflow-y-auto
          px-3
          pb-4
        "
      >
        <div className="space-y-2">

          {conversations.map(
            (conversation) => (

              <button
                key={conversation.id}

               onClick={async () => {

                setActiveConversation(
                  conversation.id
                );

                try {

                 const messages =
                   await getConversationMessages(
                    conversation.id
                   );

                 setMessages(messages);

                } catch (error) {

                  console.error(error);
                }
              }}

                className={`
                  w-full
                  rounded-xl
                  border
                  px-4
                  py-3
                  text-left
                  text-sm
                  transition-all

                  ${
                    activeConversationId ===
                    conversation.id

                      ? `
                        border-white/20
                        bg-zinc-800
                        text-white
                      `

                      : `
                        border-transparent
                        bg-zinc-900
                        text-zinc-400

                        hover:bg-zinc-800
                        hover:text-white
                      `
                  }
                `}
              >
                {conversation.title}
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );
}