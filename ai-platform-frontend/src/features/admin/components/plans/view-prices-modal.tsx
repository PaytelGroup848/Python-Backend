"use client";

import {
  usePlanPrices,
} from "@/features/admin/hooks/use-plan-prices";

import type {
  PlanPrice,
} from "@/features/admin/types/plan";

import { useState } from "react";

import {
  CreatePriceModal,
} from "./create-price-modal";

import {
  EditPriceModal,
} from "./edit-price-modal";

import {
  useDeactivatePrice,
} from "@/features/admin/hooks/use-deactivate-price";

interface Props {

  planId: number;

  onClose: () => void;
}

export function ViewPricesModal({

  planId,

  onClose,

}: Props) {

  const {
    data,
    isLoading,
    error,
  } = usePlanPrices(
    planId
  );

  const [
  showCreatePrice,
  setShowCreatePrice,
] = useState(false);

const [
  selectedPrice,
  setSelectedPrice,
] = useState<PlanPrice | null>(
  null
);

const [
  showEditPrice,
  setShowEditPrice,
] = useState(false);

const deactivatePriceMutation =
  useDeactivatePrice();

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
          w-full
          max-w-5xl
          rounded-2xl
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

  <div>

    <h2 className="text-2xl font-bold">
      Plan Pricing
    </h2>

    <p className="text-sm text-zinc-500">
      Pricing configuration for this plan
    </p>

  </div>

  <div className="flex gap-2">

    <button

      onClick={() =>
        setShowCreatePrice(
          true
        )
      }

      className="
        rounded-lg
        bg-purple-600
        px-4
        py-2
        text-white
      "
    >

      Create Price

    </button>

    <button

      onClick={onClose}

      className="
        rounded-lg
        border
        px-4
        py-2
      "
    >

      Close

    </button>

  </div>

</div>

        {isLoading && (

          <div
            className="
              py-10
              text-center
            "
          >
            Loading prices...
          </div>

        )}

        {error && (

          <div
            className="
              py-10
              text-center
              text-red-500
            "
          >
            Failed to load pricing
          </div>

        )}

        {!isLoading &&
         !error && (

          <div className="overflow-x-auto">

            <table className="w-full">

              <thead
                className="
                  border-b
                  bg-zinc-50
                "
              >

                <tr>

                  <th className="p-4 text-left">
                    Provider
                  </th>

                  <th className="p-4 text-left">
                    Currency
                  </th>

                  <th className="p-4 text-left">
                    Amount
                  </th>

                  <th className="p-4 text-left">
                    Billing Cycle
                  </th>

                  <th className="p-4 text-left">
                    External Price ID
                  </th>

                  <th className="p-4 text-left">
                    Status
                  </th>

                  <th className="p-4 text-left">
                    Actions
                  </th>

                </tr>

              </thead>

              <tbody>

                {data?.prices?.length === 0 && (

                  <tr>

                    <td
                      colSpan={7}
                      className="
                        p-8
                        text-center
                        text-zinc-500
                      "
                    >
                      No pricing found
                    </td>

                  </tr>

                )}

                {data?.prices?.map(
                  (
                    price: PlanPrice
                  ) => (

                    <tr
                      key={price.id}
                      className="border-b"
                    >

                      <td className="p-4">
                        {price.provider}
                      </td>

                      <td className="p-4">
                        {price.currency}
                      </td>

                      <td className="p-4 font-medium">
                        {price.amount}
                      </td>

                      <td className="p-4">
                        {price.billing_cycle}
                      </td>

                      <td className="p-4">
                        {price.external_price_id ?? "-"}
                      </td>

                      <td className="p-4">

                        <span
                          className={
                            price.is_active

                              ? `
                                rounded-full
                                bg-green-100
                                px-3
                                py-1
                                text-sm
                                text-green-700
                              `

                              : `
                                rounded-full
                                bg-red-100
                                px-3
                                py-1
                                text-sm
                                text-red-700
                              `
                          }
                        >
                          {price.is_active
                            ? "Active"
                            : "Inactive"}
                        </span>

                      </td>

                      <td className="p-4">

                        <div className="flex gap-2">

                          <button

                          onClick={() => {

                            setSelectedPrice(
                              price
                            );

                            setShowEditPrice(
                              true
                            );
                          }}

                          className="
                            rounded-lg
                            bg-amber-600
                            px-3
                            py-2
                            text-sm
                            text-white
                           "
                          >

                           Edit

                  </button>

    <button

      onClick={() => {

        if (
          confirm(
            "Deactivate this price?"
          )
        ) {

          deactivatePriceMutation
            .mutate(
              price.id
            );
        }
      }}

      className="
        rounded-lg
        bg-red-600
        px-3
        py-2
        text-sm
        text-white
      "
    >

      Disable

    </button>

  </div>

</td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        )}

        {showCreatePrice && (

  <CreatePriceModal

    planId={
      planId
    }

    onClose={() =>
      setShowCreatePrice(
        false
      )
    }

  />

)}

{showEditPrice &&
 selectedPrice && (

  <EditPriceModal

    price={
      selectedPrice
    }

    onClose={() =>
      setShowEditPrice(
        false
      )
    }

  />

)}

      </div>

    </div>
  );
}