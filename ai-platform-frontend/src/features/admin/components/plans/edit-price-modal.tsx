"use client";

import { useState } from "react";

import {
  useUpdatePrice,
} from "@/features/admin/hooks/use-update-price";

interface Props {

  price: {

    id: number;

    provider: string;

    currency: string;

    amount: number;

    billing_cycle: string;

    external_price_id?: string | null;
  };

  onClose: () => void;
}

export function EditPriceModal({

  price,

  onClose,

}: Props) {

  const updatePriceMutation =
    useUpdatePrice();

  const [
    provider,
    setProvider,
  ] = useState(
    price.provider
  );

  const [
    currency,
    setCurrency,
  ] = useState(
    price.currency
  );

  const [
    amount,
    setAmount,
  ] = useState(
    price.amount
  );

  const [
    billingCycle,
    setBillingCycle,
  ] = useState(
    price.billing_cycle
  );

  const [
    externalPriceId,
    setExternalPriceId,
  ] = useState(
    price.external_price_id ?? ""
  );

  const handleSubmit =
    async () => {

      try {

        await updatePriceMutation
          .mutateAsync({

            priceId:
              price.id,

            payload: {

              provider,

              currency,

              amount:
                Number(amount),

              billing_cycle:
                billingCycle,

              external_price_id:
                externalPriceId || undefined,
            },
          });

        onClose();

      } catch {

        alert(
          "Failed to update price"
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
            Edit Price
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
              Provider
            </label>

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

          </div>

          <div>

            <label
              className="
                mb-1
                block
                text-sm
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
              "
            >
              Billing Cycle
            </label>

            <input

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
              External Price ID
            </label>

            <input

              value={externalPriceId}

              onChange={(e) =>
                setExternalPriceId(
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