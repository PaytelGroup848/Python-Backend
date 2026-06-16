"use client";

import { useState } from "react";

import {
  useCreatePrice,
} from "@/features/admin/hooks/use-create-price";

interface Props {

  planId: number;

  onClose: () => void;
}

export function CreatePriceModal({

  planId,

  onClose,

}: Props) {

  const createPriceMutation =
    useCreatePrice();

  const [
    provider,
    setProvider,
  ] = useState("razorpay");

  const [
    currency,
    setCurrency,
  ] = useState("INR");

  const [
    amount,
    setAmount,
  ] = useState(0);

  const [
    billingCycle,
    setBillingCycle,
  ] = useState("monthly");

  const [
    externalPriceId,
    setExternalPriceId,
  ] = useState("");

  const handleSubmit =
    async () => {

      try {

        await createPriceMutation
          .mutateAsync({

            planId,

            payload: {

              provider,

              currency,

              amount,

              billing_cycle:
                billingCycle,

              external_price_id:
                externalPriceId || undefined,
            },
          });

        onClose();

      } catch (error) {

        console.error(
          error
        );

        alert(
          "Failed to create price"
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
            Create Price
          </h2>

          <button
            onClick={onClose}
            className="text-xl"
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
                font-medium
              "
            >
              Provider
            </label>

            <select

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
            >

              <option value="razorpay">
                Razorpay
              </option>

              <option value="stripe">
                Stripe
              </option>

            </select>

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
              Currency
            </label>

            <input

              value={currency}

              onChange={(e) =>
                setCurrency(
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
              Amount
            </label>

            <input

              type="number"

              value={amount}

              onChange={(e) =>
                setAmount(
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
              Billing Cycle
            </label>

            <select

              value={billingCycle}

              onChange={(e) =>
                setBillingCycle(
                  e.target.value
                )
              }

              className="
                w-full
                rounded-lg
                border
                p-3
              "
            >

              <option value="monthly">
                Monthly
              </option>

              <option value="yearly">
                Yearly
              </option>

            </select>

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
              External Price ID
            </label>

            <input

              value={externalPriceId}

              onChange={(e) =>
                setExternalPriceId(
                  e.target.value
                )
              }

              placeholder="Optional"

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

              disabled={
                createPriceMutation
                  .isPending
              }

              className="
                rounded-lg
                bg-purple-600
                px-4
                py-2
                text-white
              "
            >

              {createPriceMutation
                .isPending

                ? "Creating..."

                : "Create Price"}

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}