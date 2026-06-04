"use client";

import { useEffect, useState } from "react";

interface Props {

  open: boolean;

  model: any;

  onClose: () => void;

  onSubmit: (
    payload: {
      provider: string;
      description: string;
      is_active: boolean;
    }
  ) => Promise<void>;
}

export function EditModelModal({

  open,

  model,

  onClose,

  onSubmit,

}: Props) {

  const [provider, setProvider] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [isActive, setIsActive] =
    useState(true);

  useEffect(() => {

    if (model) {

      setProvider(
        model.provider || ""
      );

      setDescription(
        model.description || ""
      );

      setIsActive(
        model.is_active
      );
    }

  }, [model]);

  if (!open || !model) {
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
          Edit Model
        </h2>

        <div className="space-y-4">

          <input
            value={model.model_name}
            disabled
            className="
              w-full
              rounded-lg
              border
              bg-zinc-100
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
            className="
              w-full
              rounded-lg
              border
              p-3
            "
          />

          <label className="
            flex items-center gap-2
          ">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) =>
                setIsActive(
                  e.target.checked
                )
              }
            />

            Active
          </label>

        </div>

        <div className="
          mt-6
          flex justify-end gap-2
        ">

          <button
            onClick={onClose}
            className="
              rounded-lg
              border
              px-4 py-2
            "
          >
            Cancel
          </button>

          <button

            onClick={async () => {

              await onSubmit({

                provider,

                description,

                is_active:
                  isActive
              });

              onClose();
            }}

            className="
              rounded-lg
              bg-black
              px-4 py-2
              text-white
            "
          >
            Save
          </button>

        </div>

      </div>

    </div>
  );
}