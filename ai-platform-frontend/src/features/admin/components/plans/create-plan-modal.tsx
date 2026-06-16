"use client";

import { useState } from "react";

import {
  useCreatePlan,
} from "@/features/admin/hooks/use-create-plan";

interface Props {

  onClose: () => void;
}

export function CreatePlanModal({

  onClose,

}: Props) {

  const createPlanMutation =
    useCreatePlan();

  const [
    planCode,
    setPlanCode,
  ] = useState("");

  const [
    planName,
    setPlanName,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    isPublic,
    setIsPublic,
  ] = useState(true);

  const handleSubmit =
    async () => {

      if (
        !planCode.trim() ||
        !planName.trim()
      ) {

        alert(
          "Plan code and plan name are required"
        );

        return;
      }

      try {

        await createPlanMutation
          .mutateAsync({

            plan_code:
              planCode,

            plan_name:
              planName,

            description:
              description,

            is_public:
              isPublic,
          });

        onClose();

      } catch (error) {

        console.error(
          error
        );

        alert(
          "Failed to create plan"
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
            Create Plan
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
              Plan Code
            </label>

            <input
              value={
                planCode
              }
              onChange={(e) =>
                setPlanCode(
                  e.target.value
                )
              }
              placeholder="pro"
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
              Plan Name
            </label>

            <input
              value={
                planName
              }
              onChange={(e) =>
                setPlanName(
                  e.target.value
                )
              }
              placeholder="Pro Plan"
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
              Description
            </label>

            <textarea
              value={
                description
              }
              onChange={(e) =>
                setDescription(
                  e.target.value
                )
              }
              rows={4}
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
              items-center
              gap-2
            "
          >

            <input
              type="checkbox"
              checked={
                isPublic
              }
              onChange={(e) =>
                setIsPublic(
                  e.target.checked
                )
              }
            />

            <span>
              Public Plan
            </span>

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
                createPlanMutation.isPending
              }

              className="
                rounded-lg
                bg-black
                px-4
                py-2
                text-white
              "
            >

              {createPlanMutation
                .isPending
                  ? "Creating..."
                  : "Create Plan"}

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}