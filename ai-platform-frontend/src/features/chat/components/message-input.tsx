"use client";

import { useState } from "react";

import { Send } from "lucide-react";

interface MessageInputProps {
  onSend: (
    message: string
  ) => void;
}

export function MessageInput({
  onSend,
}: MessageInputProps) {

  const [message, setMessage] =
    useState("");

  function handleSend() {

    if (!message.trim()) {
      return;
    }

    onSend(message);

    setMessage("");
  }

  return (
    <div
      className="
        flex
        items-center
        gap-3
        rounded-2xl
        border
        border-white/10
        bg-zinc-900
        p-3
      "
    >
      <textarea
        value={message}
        onChange={(e) =>
          setMessage(e.target.value)
        }
        placeholder="
          Ask your AI assistant...
        "
        rows={1}
        className="
          flex-1
          resize-none
          bg-transparent
          text-base
          text-white
          outline-none
          placeholder:text-zinc-400
        "
      />

      <button
        onClick={handleSend}
        aria-label="Send message"
        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-xl
          bg-white
          text-black
          transition-all
          hover:scale-105
        "
      >
        <Send className="h-4 w-4" />
      </button>
    </div>
  );
}