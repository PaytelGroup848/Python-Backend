"use client";

import {
  useSubscriptions,
} from "@/features/admin/hooks/use-subscriptions";

import {
  useActivateSubscription,
} from "@/features/admin/hooks/use-activate-subscription";

import {
  useCancelSubscription,
} from "@/features/admin/hooks/use-cancel-subscription";

export default function SubscriptionsPage() {

  const {
    data,
    isLoading,
    error,
  } = useSubscriptions();

  const activateMutation =
    useActivateSubscription();

  const cancelMutation =
    useCancelSubscription();

  if (isLoading) {

    return (
      <div className="p-6">
        Loading subscriptions...
      </div>
    );
  }

  if (error) {

    return (
      <div className="p-6">
        Failed to load subscriptions
      </div>
    );
  }

  return (

    <div className="space-y-6">

      <div>

        <h1 className="text-3xl font-bold">
          Subscription Management
        </h1>

        <p className="text-zinc-500">
          Manage user subscriptions
        </p>

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
                User
              </th>

              <th className="p-4 text-left">
                Plan
              </th>

              <th className="p-4 text-left">
                Status
              </th>

              <th className="p-4 text-left">
                Token Limit
              </th>

              <th className="p-4 text-left">
                Auto Renew
              </th>

              <th className="p-4 text-left">
                Start Date
              </th>

              <th className="p-4 text-left">
                End Date
              </th>

              <th className="p-4 text-left">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {data?.subscriptions?.map(
              subscription => (

                <tr
                  key={subscription.id}
                  className="border-b"
                >

                  <td className="p-4">
                    {subscription.id}
                  </td>

                  <td className="p-4">
                    {subscription.user_id}
                  </td>

                  <td className="p-4">
                    {subscription.plan_name}
                  </td>

                  <td className="p-4">

                    <span
                      className={
                        subscription.status ===
                        "active"

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

                      {subscription.status}

                    </span>

                  </td>

                  <td className="p-4">
                    {subscription.monthly_token_limit?.toLocaleString() ?? "-"}
                  </td>

                  <td className="p-4">
                    {subscription.auto_renew
                      ? "Yes"
                      : "No"}
                  </td>

                  <td className="p-4">
                    {subscription.start_date
                      ? new Date(
                          subscription.start_date
                        ).toLocaleDateString()
                      : "-"}
                  </td>

                  <td className="p-4">
                    {subscription.end_date
                      ? new Date(
                          subscription.end_date
                        ).toLocaleDateString()
                      : "-"}
                  </td>

                  <td className="p-4">

                    <div className="flex gap-2">

                      <button

                        onClick={() =>
                          activateMutation
                            .mutate(
                              subscription.id
                            )
                        }

                        className="
                          rounded-lg
                          bg-green-600
                          px-3
                          py-2
                          text-sm
                          text-white
                        "
                      >

                        Activate

                      </button>

                      <button

                        onClick={() =>
                          cancelMutation
                            .mutate(
                              subscription.id
                            )
                        }

                        className="
                          rounded-lg
                          bg-red-600
                          px-3
                          py-2
                          text-sm
                          text-white
                        "
                      >

                        Cancel

                      </button>

                    </div>

                  </td>

                </tr>
              )
            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}