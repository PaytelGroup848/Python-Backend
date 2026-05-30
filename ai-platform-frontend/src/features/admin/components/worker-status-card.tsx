"use client";

import {
  useWorkers,
} from "../hooks/use-workers";

export function WorkerStatusCard() {

  const {
    data,
    isLoading,
    error,
  } = useWorkers();

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
        Loading workers...
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
        Failed to load workers
      </div>
    );
  }

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
          Worker Status
        </h2>

        <p className="text-sm text-zinc-500">
          Background processing workers
        </p>

      </div>

      <div className="space-y-4">

        {data?.workers.map(
          (worker) => (

            <div
              key={worker.name}
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
              <div className="flex items-center gap-3">

                <div
                  className={`
                    h-3
                    w-3
                    rounded-full
                    ${
                      worker.status ===
                      "running"
                        ? "bg-green-500"
                        : "bg-red-500"
                    }
                  `}
                />

                <div>

                  <div className="font-medium">
                    {worker.name}
                  </div>

                  <div
                    className="
                      text-xs
                      text-zinc-500
                    "
                  >
                    Queue Size:{" "}
                    {worker.queue_size}
                  </div>

                </div>

              </div>

              <span
                className="
                  rounded-full
                  bg-green-100
                  px-3
                  py-1
                  text-sm
                  font-medium
                  text-green-700
                "
              >
                {worker.status}
              </span>
            </div>
          )
        )}

      </div>
    </div>
  );
}