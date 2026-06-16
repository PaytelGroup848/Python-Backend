"use client";

import { useState } from "react";

import {
  useUpdateVersion,
} from "@/features/admin/hooks/use-update-version";

interface Props {

  version: {

    id: number;

    monthly_token_limit: number;

    monthly_request_limit: number;

    monthly_cost_limit?: number;
  };

  onClose: () => void;
}

export function EditVersionModal({

  version,

  onClose,

}: Props) {

  const updateVersionMutation =
    useUpdateVersion();

  const [
    monthlyTokenLimit,
    setMonthlyTokenLimit,
  ] = useState(
    version.monthly_token_limit
  );

  const [
    monthlyRequestLimit,
    setMonthlyRequestLimit,
  ] = useState(
    version.monthly_request_limit
  );

  const [
    monthlyCostLimit,
    setMonthlyCostLimit,
  ] = useState(
    version.monthly_cost_limit ?? 0
  );

  const handleSubmit =
    async () => {

      try {

        await updateVersionMutation
          .mutateAsync({

            versionId:
              version.id,

            payload: {

              monthly_token_limit:
                monthlyTokenLimit,

              monthly_request_limit:
                monthlyRequestLimit,

              monthly_cost_limit:
                monthlyCostLimit,
            },
          });

        onClose();

      } catch {

        alert(
          "Failed to update version"
        );
      }
    };

  return (

    <div
      className="
        fixed
        inset-0
        z-50
        flex
        items-center
        justify-center
        bg-black/50
      "
    >

      <div
        className="
          w-[600px]
          rounded-xl
          bg-white
          p-6
        "
      >

        <div
          className="
            mb-6
            flex
            items-center
            justify-between
          "
        >

          <h2
            className="
              text-2xl
              font-bold
            "
          >
            Edit Version
          </h2>

          <button
            onClick={onClose}
          >
            ✕
          </button>

        </div>

        <div className="space-y-4">

          <div>

            <label
              className="
                mb-1
                block
                text-sm
              "
            >
              Monthly Token Limit
            </label>

            <input

              type="number"

              value={
                monthlyTokenLimit
              }

              onChange={(e) =>
                setMonthlyTokenLimit(
                  Number(
                    e.target.value
                  )
                )
              }

              className="
                w-full
                rounded-lg
                border
                p-3
              "
            />

          </div>

          <div>

            <label
              className="
                mb-1
                block
                text-sm
              "
            >
              Monthly Request Limit
            </label>

            <input

              type="number"

              value={
                monthlyRequestLimit
              }

              onChange={(e) =>
                setMonthlyRequestLimit(
                  Number(
                    e.target.value
                  )
                )
              }

              className="
                w-full
                rounded-lg
                border
                p-3
              "
            />

          </div>

          <div>

            <label
              className="
                mb-1
                block
                text-sm
              "
            >
              Monthly Cost Limit
            </label>

            <input

              type="number"

              value={
                monthlyCostLimit
              }

              onChange={(e) =>
                setMonthlyCostLimit(
                  Number(
                    e.target.value
                  )
                )
              }

              className="
                w-full
                rounded-lg
                border
                p-3
              "
            />

          </div>

          <div
            className="
              flex
              justify-end
              gap-3
              pt-4
            "
          >

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

              onClick={
                handleSubmit
              }

              className="
                rounded-lg
                bg-amber-600
                px-4
                py-2
                text-white
              "
            >
              Save Changes
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}