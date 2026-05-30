"use client";

import {
  useQueues,
} from "../hooks/use-queues";

export function QueueStatusCard() {

  const {
    data,
    isLoading,
    error,
  } = useQueues();

  if (isLoading) {

    return (
      <div
        className="
          rounded-2xl
          border
          border-zinc-200
          bg-white
          p-6
          shadow-sm
        "
      >
        Loading queues...
      </div>
    );
  }

  if (error) {

    return (
      <div
        className="
          rounded-2xl
          border
          border-red-200
          bg-white
          p-6
          shadow-sm
        "
      >
        Failed to load queues
      </div>
    );
  }

  const queues = [
    {
      name: "Chat Queue",
      count: data?.chat_queue ?? 0,
    },
    {
      name: "Embedding Queue",
      count: data?.embedding_queue ?? 0,
    },
    {
      name: "RAG Queue",
      count: data?.rag_queue ?? 0,
    },
    {
      name: "Voice Queue",
      count: data?.voice_queue ?? 0,
    },
  ];

  return (
    <div
      className="
        rounded-2xl
        border
        border-zinc-200
        bg-white
        p-6
        shadow-sm
      "
    >
      <div className="mb-6">

        <h2 className="text-xl font-semibold">
          Queue Status
        </h2>

        <p className="text-sm text-zinc-500">
          Redis stream monitoring
        </p>

      </div>

      <div className="space-y-4">

        {queues.map((queue) => (

          <div
            key={queue.name}
            className="
              flex
              items-center
              justify-between
              rounded-lg
              border
              border-zinc-100
              p-3
            "
          >
            <span className="font-medium">
              {queue.name}
            </span>

            <span
              className="
                rounded-full
                bg-zinc-100
                px-3
                py-1
                text-sm
                font-medium
              "
            >
              {queue.count}
            </span>
          </div>

        ))}

      </div>
    </div>
  );
}