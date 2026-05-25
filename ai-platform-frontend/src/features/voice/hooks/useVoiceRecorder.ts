"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

export function useVoiceRecorder() {

  const mediaRecorderRef =
    useRef<MediaRecorder | null>(
      null
    );

  const websocketRef =
    useRef<WebSocket | null>(
      null
    );

  const [isRecording, setIsRecording] =
    useState(false);

  const [transcript, setTranscript] =
    useState("");

  async function startRecording() {

    try {

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      const mimeType =
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus"
        )
          ? "audio/webm;codecs=opus"
          : "";

      const mediaRecorder =
        mimeType
          ? new MediaRecorder(stream, {
              mimeType,
            })
          : new MediaRecorder(stream);

      mediaRecorderRef.current =
        mediaRecorder;

      const ws =
        new WebSocket(
          `${process.env.NEXT_PUBLIC_WS_URL}/ws/voice`
        );

      websocketRef.current = ws;

      ws.onopen = () => {

        console.log(
          "Voice websocket connected"
        );

        console.log(
          "Starting media recorder"
        );

        mediaRecorder.start(250);

        setIsRecording(true);
      };

      mediaRecorder.ondataavailable =
        async (event) => {

          console.log(
            "Sending audio chunk",
            event.data.size
          );

          if (
            event.data.size > 0 &&
            ws.readyState === WebSocket.OPEN
          ) {

            const arrayBuffer =
              await event.data.arrayBuffer();

            ws.send(arrayBuffer);
          }
        };

      ws.onmessage = (event) => {

        try {

          const data =
            JSON.parse(event.data);

          console.log(
            "Server message:",
            data
          );

          if (
            data.type === "transcript"
          ) {

            console.log(
              "Transcript:",
              data.text
            );

            setTranscript(data.text);
          }

        } catch (error) {

          console.error(
            "Message parse error",
            error
          );
        }
      };

      ws.onerror = (error) => {

        console.error(
          "Voice websocket error",
          error
        );
      };

      ws.onclose = () => {

        console.log(
          "Voice websocket closed"
        );
      };

    } catch (error) {

      console.error(
        "Voice recording error",
        error
      );
    }
  }

  function stopRecording() {

    mediaRecorderRef.current?.stop();

    websocketRef.current?.close();

    setIsRecording(false);
  }

  useEffect(() => {

    return () => {

      websocketRef.current?.close();
    };

  }, []);

  return {
    isRecording,
    transcript,
    startRecording,
    stopRecording,
  };
}