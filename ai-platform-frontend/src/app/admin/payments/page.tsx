"use client";

import {
  usePayments,
} from "@/features/admin/hooks/use-payments";

export default function PaymentsPage() {

  const {
    data,
    isLoading,
    error,
  } = usePayments();

  if (isLoading) {

    return (
      <div className="p-6">
        Loading payments...
      </div>
    );
  }

  if (error) {

    return (
      <div className="p-6">
        Failed to load payments
      </div>
    );
  }

  return (

    <div className="space-y-6">

      <div>

        <h1 className="text-3xl font-bold">
          Payments Management
        </h1>

        <p className="text-zinc-500">
          Monitor platform payments
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
                Reference
              </th>

              <th className="p-4 text-left">
                User
              </th>

              <th className="p-4 text-left">
                Provider
              </th>

              <th className="p-4 text-left">
                Type
              </th>

              <th className="p-4 text-left">
                Amount
              </th>

              <th className="p-4 text-left">
                Currency
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

            {data?.payments?.map(
              payment => (

                <tr
                  key={payment.id}
                  className="border-b"
                >

                  <td className="p-4">
                    {payment.id}
                  </td>

                  <td className="p-4">
                    {payment.payment_reference}
                  </td>

                  <td className="p-4">
                    {payment.user_id}
                  </td>

                  <td className="p-4">
                    {payment.provider}
                  </td>

                  <td className="p-4">
                    {payment.payment_type}
                  </td>

                  <td className="p-4 font-medium">
                    {payment.amount}
                  </td>

                  <td className="p-4">
                    {payment.currency}
                  </td>

                  <td className="p-4">

                    <span
                      className={
                        payment.status === "paid"

                          ? `
                            rounded-full
                            bg-green-100
                            px-3
                            py-1
                            text-sm
                            text-green-700
                          `

                          : payment.status === "failed"

                          ? `
                            rounded-full
                            bg-red-100
                            px-3
                            py-1
                            text-sm
                            text-red-700
                          `

                          : `
                            rounded-full
                            bg-yellow-100
                            px-3
                            py-1
                            text-sm
                            text-yellow-700
                          `
                      }
                    >

                      {payment.status}

                    </span>

                  </td>

                  <td className="p-4">

                    {new Date(
                      payment.created_at
                    ).toLocaleDateString()}

                  </td>

                  <td className="p-4">

                    <button
                      className="
                        rounded-lg
                        bg-blue-600
                        px-3
                        py-2
                        text-sm
                        text-white
                     "
                    >

                    View

                    </button>

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