"use client";

import {
  useProviders,
} from "../hooks/use-providers";

export function ProviderStatusCard() {

  const {
    data,
    isLoading,
    error,
  } = useProviders();

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
        Loading providers...
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
        Failed to load providers
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
          Provider Health
        </h2>

        <p className="text-sm text-zinc-500">
          LLM provider monitoring
        </p>

      </div>

      <div className="space-y-4">

        {data?.providers.map(
          (provider) => (

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
                  className={`
                    h-3
                    w-3
                    rounded-full
                    ${
                      provider.status ===
                      "healthy"
                        ? "bg-green-500"
                        : "bg-red-500"
                    }
                  `}
                />

                <div>

                  <div className="font-medium">
                    {provider.name}
                  </div>

                  <div
                    className="
                      text-xs
                      text-zinc-500
                    "
                  >
                    {provider.latency_ms} ms
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
                {provider.status}
              </span>
            </div>
          )
        )}

      </div>
    </div>
  );
}