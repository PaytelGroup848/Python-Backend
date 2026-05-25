"use client";

import {
  Mic,
  Square,
} from "lucide-react";

import {
  useVoiceRecorder,
} from "../hooks/useVoiceRecorder";

interface VoiceButtonProps {
  isRecording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
}

export function VoiceButton({
  isRecording,
  startRecording,
  stopRecording,
}: VoiceButtonProps) {

  return (

    <button
      onClick={() => {

        if (isRecording) {

          stopRecording();

        } else {

          startRecording();
        }
      }}

      className={`
        shrink-0
        flex
        h-10
        w-10
        items-center
        justify-center
        rounded-xl
        transition-all
        ${
          isRecording
            ? "bg-red-500 text-white"
            : `
              bg-zinc-200
              text-zinc-900
              dark:bg-zinc-800
              dark:text-white
            `
        }
      `}
    >

      {isRecording ? (
        <Square className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}

    </button>
  );
}