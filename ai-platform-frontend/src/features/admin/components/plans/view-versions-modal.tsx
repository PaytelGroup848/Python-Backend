"use client";

import {
  usePlanVersions,
} from "@/features/admin/hooks/use-plan-versions";

import type {
  PlanVersion,
} from "@/features/admin/types/plan";

import { useState } from "react";

import {
  CreateVersionModal,
} from "./create-version-modal";

import {
  EditVersionModal,
} from "./edit-version-modal";

interface Props {

  planId: number;

  onClose: () => void;
}

export function ViewVersionsModal({

  planId,

  onClose,

}: Props) {

  const {
    data,
    isLoading,
    error,
  } = usePlanVersions(
    planId
  );

  const [
  showCreateVersion,
  setShowCreateVersion,
] = useState(false);

const [
  selectedVersion,
  setSelectedVersion,
] = useState<PlanVersion | null>(
  null
);

const [
  showEditVersion,
  setShowEditVersion,
] = useState(false);

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
      Plan Versions
    </h2>

    <p className="text-sm text-zinc-500">
      Version history and limits
    </p>

  </div>

  <div className="flex gap-2">

    <button

      onClick={() =>
        setShowCreateVersion(
          true
        )
      }

      className="
        rounded-lg
        bg-blue-600
        px-4
        py-2
        text-white
      "
    >
      Create Version
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
            Loading versions...
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
            Failed to load versions
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
                    Version
                  </th>

                  <th className="p-4 text-left">
                    Monthly Tokens
                  </th>

                  <th className="p-4 text-left">
                    Monthly Requests
                  </th>

                  <th className="p-4 text-left">
                    Monthly Cost Limit
                  </th>

                  <th className="p-4 text-left">
                    Status
                  </th>

                  <th className="p-4 text-left">
                    Created
                  </th>

                  <th className="p-4 text-left">
                    Actions
                  </th>

                </tr>

              </thead>

              <tbody>

                {data?.versions?.length === 0 && (

                  <tr>

                    <td
                      colSpan={7}
                      className="
                        p-8
                        text-center
                        text-zinc-500
                      "
                    >
                      No versions found
                    </td>

                  </tr>

                )}

                {data?.versions?.map(
                  (
                    version: PlanVersion
                  ) => (

                    <tr
                      key={version.id}
                      className="border-b"
                    >

                      <td className="p-4 font-medium">
                        v{version.version_number}
                      </td>

                      <td className="p-4">
                        {version.monthly_token_limit.toLocaleString()}
                      </td>

                      <td className="p-4">
                        {version.monthly_request_limit.toLocaleString()}
                      </td>

                      <td className="p-4">
                        {version.monthly_cost_limit?.toLocaleString()}
                      </td>

                      <td className="p-4">

                        <span
                          className={
                            version.is_active

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
                          {version.is_active
                            ? "Active"
                            : "Inactive"}
                        </span>

                      </td>

                      <td className="p-4">

                        {new Date(
                          version.created_at
                        ).toLocaleDateString()}

                      </td>

                      <td className="p-4">

                        <button

                          onClick={() => {

                            setSelectedVersion(
                              version
                            );

                            setShowEditVersion(
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

                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        )}

        {showCreateVersion && (

  <CreateVersionModal

    planId={
      planId
    }

    onClose={() =>
      setShowCreateVersion(
        false
      )
    }

  />

)}

{showEditVersion &&
 selectedVersion && (

  <EditVersionModal

    version={
      selectedVersion
    }

    onClose={() =>
      setShowEditVersion(
        false
      )
    }

  />

)}

      </div>

    </div>
  );
}