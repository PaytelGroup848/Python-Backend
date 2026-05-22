"use client";

import {
  useRef,
  useState,
} from "react";

import {
  Send,
  Upload,
} from "lucide-react";

import {
  uploadDocument,
} from "@/features/documents/services/document-service";

import {
  useDocumentStore,
} from "@/features/documents/stores/document-store";

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

  const inputRef =
    useRef<HTMLInputElement>(null);

  const [uploading, setUploading] =
    useState(false);

  const addDocument =
    useDocumentStore(
      (state) =>
        state.addDocument
    );

  const documents =
    useDocumentStore(
      (state) =>
        state.documents
    );

  async function handleUpload(
    file: File
  ) {

    try {

      setUploading(true);

      await uploadDocument(
        file
      );

      alert(
        "Document uploaded successfully"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Upload failed"
      );

    } finally {

      setUploading(false);
    }
  }

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
        type="button"

        onClick={() =>
          inputRef.current?.click()
        }

        disabled={uploading}

        className="
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-xl
          border
          border-white/10
          bg-zinc-800
          text-w hite
          transition-all
          hover:bg-zinc-700
          disabled:opacity-50
        "
      >
        <Upload className="h-4 w-4" />
      </button>

      <input
        ref={inputRef}

        type="file"

        accept="
          .pdf,
          .docx,
          .txt,
          .csv,
          .xlsx,
          .pptx,
          .png,
          .jpg,
          .jpeg
        "

        className="hidden"

        onChange={(e) => {

        const file =
          e.target.files?.[0];

        if (file) {

          handleUpload(file);
        }
      }}
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