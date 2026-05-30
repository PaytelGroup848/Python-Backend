export function WorkerStatusCard() {
  const workers = [
    {
      name: "Chat Request Worker",
      status: "Running",
    },
    {
      name: "Chat Response Worker",
      status: "Running",
    },
    {
      name: "Embedding Worker",
      status: "Running",
    },
    {
      name: "RAG Worker",
      status: "Running",
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
          Worker Status
        </h2>

        <p className="text-sm text-zinc-500">
          Background processing workers
        </p>
      </div>

      <div className="space-y-4">
        {workers.map((worker) => (
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
                className="
                  h-3
                  w-3
                  rounded-full
                  bg-green-500
                "
              />

              <span className="font-medium">
                {worker.name}
              </span>

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
        ))}
      </div>
    </div>
  );
}