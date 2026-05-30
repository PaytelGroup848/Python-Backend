"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Send,
  Upload,
  X,
} from "lucide-react";

import {
  uploadDocument,
} from "@/features/documents/services/document-service";

import {
  useDocumentStore,
} from "@/features/documents/stores/document-store";
import {
  VoiceButton,
} from "@/features/voice/components/voice-button";

import {
  useVoiceRecorder,
} from "@/features/voice/hooks/useVoiceRecorder";

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

  const {
    isRecording,
    transcript,
    startRecording,
    stopRecording,
  } = useVoiceRecorder();

  useEffect(() => {

  if (!transcript) {
    return;
  }

  const timeout = setTimeout(() => {

    setMessage((prev) => {

      if (!prev) {
        return transcript;
      }

      if (
        prev.includes(transcript)
      ) {
        return prev;
      }

      return `${prev} ${transcript}`;
    });

  }, 0);

  return () =>
    clearTimeout(timeout);

}, [transcript]);

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

  const removeDocument =
    useDocumentStore(
      (state) =>
        state.removeDocument
    );

  async function handleUpload(
    file: File
  ) {

    try {

      setUploading(true);

      const response =
        await uploadDocument(
          file
        );

      addDocument({
        filename:
          response.filename,
        status:
          "uploaded",
      });

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

  <div className="flex flex-col gap-3">

    {/* DOCUMENTS */}

    {documents.length > 0 && (

      <div className="flex flex-wrap gap-2">

        {documents.map((doc) => (

          <div
            key={doc.filename}

            className="
              flex
              items-center
              gap-2
              rounded-xl
              border
              border-zinc-200
              bg-white
              px-3
              py-2
              text-sm
              text-zinc-800
              dark:border-white/10
              dark:bg-zinc-800
              dark:text-white
            "
          >
            <span>
             📄 {doc.filename}
            </span>

            <button
              onClick={() =>
                removeDocument(
                  doc.filename
                )
              }

              className="
                text-zinc-400
                transition-colors
                hover:text-red-400
              "
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    )}

    {/* INPUT */}

    <div className="relative">

      

      <div
        className="
          flex
          items-center
          gap-3
          rounded-2xl
          border
          border-zinc-200
          bg-white
          p-3
          dark:border-white/10
          dark:bg-zinc-900
        "
      > 
      <textarea
        value={message}
        onChange={(e) =>
          setMessage(e.target.value)
        }
        onInput={(e) => {

          e.currentTarget.style.height = "auto";

          e.currentTarget.style.height =
            `${e.currentTarget.scrollHeight}px`;
        }}
        placeholder="
          Ask your AI assistant...
        "
        rows={1}
        className="
          flex-1
          resize-none
          bg-transparent
          text-base
          text-zinc-900
          outline-none
          placeholder:text-zinc-500
          dark:text-white
          dark:placeholder:text-zinc-400
        "
      />

      <button
        type="button"

        onClick={() =>
          inputRef.current?.click()
        }

        disabled={uploading}

        className="
          shrink-0
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-xl
          border
          border-zinc-200
          bg-white
          text-zinc-800
          transition-all
          hover:bg-zinc-100
          disabled:opacity-50
          dark:border-white/10
          dark:bg-zinc-800
          dark:text-white
          dark:hover:bg-zinc-700
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

      <VoiceButton
        isRecording={isRecording}
        startRecording={startRecording}
        stopRecording={stopRecording}
      />

      <button
        onClick={handleSend}
        aria-label="Send message"
        className="
          shrink-0
          flex
          h-10
          w-10
          items-center
          justify-center
          rounded-xl
          bg-black
          text-white
          transition-all
          hover:scale-105
          dark:bg-white
          dark:text-black
        "
      >
        
        <Send className="h-4 w-4" />
      </button>
      </div>

    </div>

  </div>
  );
}