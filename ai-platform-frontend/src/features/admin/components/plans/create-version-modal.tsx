"use client";

import { useState } from "react";

import {
  useCreateVersion,
} from "@/features/admin/hooks/use-create-version";

interface Props {

  planId: number;

  onClose: () => void;
}

export function CreateVersionModal({

  planId,

  onClose,

}: Props) {

  const createVersionMutation =
    useCreateVersion();

  const [
    versionNumber,
    setVersionNumber,
  ] = useState(1);

  const [
    monthlyTokenLimit,
    setMonthlyTokenLimit,
  ] = useState(0);

  const [
    monthlyRequestLimit,
    setMonthlyRequestLimit,
  ] = useState(0);

  const [
    monthlyCostLimit,
    setMonthlyCostLimit,
  ] = useState(0);

  const handleSubmit =
    async () => {

      try {

        await createVersionMutation
          .mutateAsync({

            planId,

            payload: {

              version_number:
                versionNumber,

              monthly_token_limit:
                monthlyTokenLimit,

              monthly_request_limit:
                monthlyRequestLimit,

              monthly_cost_limit:
                monthlyCostLimit,
            },
          });

        onClose();

      } catch (error) {

        console.error(
          error
        );

        alert(
          "Failed to create version"
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
          w-[650px]
          rounded-xl
          bg-white
          p-6
          shadow-xl
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
            Create Version
          </h2>

          <button
            onClick={
              onClose
            }
            className="
              text-xl
            "
          >
            ✕
          </button>

        </div>

        <div
          className="
            space-y-4
          "
        >

          <div>

            <label
              className="
                mb-1
                block
                text-sm
                font-medium
              "
            >
              Version Number
            </label>

            <input
              type="number"
              value={
                versionNumber
              }
              onChange={(e) =>
                setVersionNumber(
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
                font-medium
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
                font-medium
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
                font-medium
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
              onClick={
                onClose
              }
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

              disabled={
                createVersionMutation
                  .isPending
              }

              className="
                rounded-lg
                bg-blue-600
                px-4
                py-2
                text-white
              "
            >

              {createVersionMutation
                .isPending
                  ? "Creating..."
                  : "Create Version"}

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}