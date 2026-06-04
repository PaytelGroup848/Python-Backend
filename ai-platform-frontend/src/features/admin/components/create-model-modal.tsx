"use client";

import { useState } from "react";

interface Props {

  open: boolean;

  onClose: () => void;

  onSubmit: (
    payload: {
      model_name: string;
      provider: string;
      description: string;
    }
  ) => Promise<void>;
}

export function CreateModelModal({

  open,

  onClose,

  onSubmit

}: Props) {

  const [modelName, setModelName] =
    useState("");

  const [provider, setProvider] =
    useState("");

  const [description, setDescription] =
    useState("");

  if (!open) {
    return null;
  }

  return (

    <div className="
      fixed inset-0
      bg-black/50
      flex items-center
      justify-center
      z-50
    ">

      <div className="
        w-full
        max-w-lg
        rounded-xl
        bg-white
        p-6
      ">

        <h2 className="
          mb-4
          text-xl
          font-semibold
        ">
          Create Model
        </h2>

        <div className="space-y-4">

          <input
            value={modelName}
            onChange={(e) =>
              setModelName(
                e.target.value
              )
            }
            placeholder="Model Name"
            className="
              w-full
              rounded-lg
              border
              p-3
            "
          />

          <input
            value={provider}
            onChange={(e) =>
              setProvider(
                e.target.value
              )
            }
            placeholder="Provider"
            className="
              w-full
              rounded-lg
              border
              p-3
            "
          />

          <textarea
            value={description}
            onChange={(e) =>
              setDescription(
                e.target.value
              )
            }
            placeholder="Description"
            className="
              w-full
              rounded-lg
              border
              p-3
            "
          />

        </div>

        <div className="
          mt-6
          flex
          justify-end
          gap-2
        ">

          <button
            onClick={onClose}
            className="
              rounded-lg
              border
              px-4
              py-2
            "
          >
            Cancel
          </button>

          <button

            onClick={async () => {

              await onSubmit({

                model_name:
                  modelName,

                provider,

                description
              });

              onClose();
            }}

            className="
              rounded-lg
              bg-black
              px-4
              py-2
              text-white
            "
          >
            Create
          </button>

        </div>

      </div>

    </div>
  );
}