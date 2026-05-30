export function ProviderStatusCard() {
  const providers = [
    {
      name: "OpenAI",
      status: "Healthy",
    },
    {
      name: "Groq",
      status: "Healthy",
    },
    {
      name: "Mistral",
      status: "Healthy",
    },
    {
      name: "Claude",
      status: "Healthy",
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
          Provider Health
        </h2>

        <p className="text-sm text-zinc-500">
          LLM provider monitoring
        </p>
      </div>

      <div className="space-y-4">
        {providers.map((provider) => (
          <div
            key={provider.name}
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
                {provider.name}
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
              {provider.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}