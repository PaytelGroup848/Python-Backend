"use client";

import { useState } from "react";

import {
  ViewVersionsModal,
} from "@/features/admin/components/plans/view-versions-modal";

import {
  usePlans,
} from "@/features/admin/hooks/use-plans";

import {
  ViewPricesModal,
} from "@/features/admin/components/plans/view-prices-modal";

import {
  CreatePlanModal,
} from "@/features/admin/components/plans/create-plan-modal";

export default function PlansPage() {

  const {
    data,
    isLoading,
    error,
  } = usePlans();

  const [
    selectedPlanId,
    setSelectedPlanId
   ] = useState<number | null>(
    null
   );

  const [
    showVersions,
    setShowVersions
   ] = useState(false);


  const [showPrices, setShowPrices] =
    useState(false);

 const [showCreatePlan, setShowCreatePlan,
   ] = useState(false);

 

  if (isLoading) {

    return (
      <div className="p-6">
        Loading plans...
      </div>
    );
  }

  if (error) {

    return (
      <div className="p-6">
        Failed to load plans
      </div>
    );
  }

  return (
    <div className="space-y-6">

      <div
        className="
          flex
          items-center
          justify-between
        "
    >   

      <div>

        <h1 className="text-3xl font-bold">
            Plans Management
        </h1>

        <p className="text-zinc-500">
            Manage platform plans
        </p>

      </div>

      <button
        onClick={() =>
          setShowCreatePlan(true)
        }
        className="
        rounded-lg
        bg-black
        px-4
        py-2
        text-white
       "
    >
      Create Plan
    </button>

    </div>

      <div
        className="
          overflow-hidden
          rounded-2xl
          border
          bg-white
          shadow-sm
        "
      >

        <table className="w-full">

          <thead
            className="
              border-b
              bg-zinc-50
            "
          >
            <tr>

              <th className="p-4 text-left">
                ID
              </th>

              <th className="p-4 text-left">
                Code
              </th>

              <th className="p-4 text-left">
                Name
              </th>

              <th className="p-4 text-left">
                Description
              </th>

              <th className="p-4 text-left">
                Public
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

            {data?.plans.map(plan => (

              <tr
                key={plan.id}
                className="border-b"
              >

                <td className="p-4">
                  {plan.id}
                </td>

                <td className="p-4">
                  {plan.plan_code}
                </td>

                <td className="p-4">
                  {plan.plan_name}
                </td>

                <td className="p-4">
                  {plan.description}
                </td>

                <td className="p-4">
                  {plan.is_public
                    ? "Yes"
                    : "No"}
                </td>

                <td className="p-4">

                  <span
                    className={
                      plan.is_active
                        ? "text-green-600"
                        : "text-red-600"
                    }
                  >
                    {plan.is_active
                      ? "Active"
                      : "Inactive"}
                  </span>

                </td>

                <td className="p-4">

                  <div className="flex gap-2">

                    <button

                      onClick={() => {

                        setSelectedPlanId(
                           plan.id
                        );

                        setShowVersions(
                          true
                        );
                      }}

                     className="
                    rounded-lg
                    bg-blue-600
                    px-3
                    py-2
                    text-sm
                    text-white
                  "
                >

                 Versions

                </button>
                    <button

                      onClick={() => {

                        setSelectedPlanId(
                            plan.id
                        );

                        setShowPrices(
                          true
                        );
                    }}

                    className="
                      rounded-lg
                      bg-purple-600
                       px-3
                       py-2
                       text-sm
                       text-white
                      "
                    >

                      Prices

                    </button>

                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>
      {showVersions &&
      selectedPlanId && (

      <ViewVersionsModal

       planId={
        selectedPlanId
       }

       onClose={() =>
        setShowVersions(false)
      }
    />
  )}

  {showPrices &&
 selectedPlanId && (

  <ViewPricesModal

    planId={
      selectedPlanId
    }

    onClose={() =>
      setShowPrices(false)
    }
  />
)}

{showCreatePlan && (

  <CreatePlanModal

    onClose={() =>
      setShowCreatePlan(
        false
      )
    }

  />

)}

    </div>
  );
}