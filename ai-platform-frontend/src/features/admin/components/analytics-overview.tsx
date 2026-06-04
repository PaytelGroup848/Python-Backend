"use client";

import {
  Activity,
  Clock3,
  Users,
  Bot,
  KeyRound
} from "lucide-react";

import {
  useAnalytics
} from "../hooks/use-analytics";

import {
  AnalyticsCharts
} from "./analytics-charts";

export function AnalyticsOverview() {

  const {

    data,

    loading

  } = useAnalytics();

  if (
    loading ||
    !data
  ) {

    return (
      <div>
        Loading...
      </div>
    );
  }

  return (

    <div className="space-y-6">

      {/* Stats Cards */}

      <div className="
        grid
        gap-4
        md:grid-cols-5
      ">

        <div className="
          rounded-xl
          border
          bg-white
          p-5
          shadow-sm
        ">

          <div className="
            flex
            items-center
            justify-between
          ">

            <div>

              <p className="
                text-sm
                text-zinc-500
              ">
                Total Requests
              </p>

              <h2 className="
                mt-2
                text-3xl
                font-bold
              ">
                {data.total_requests}
              </h2>

            </div>

            <Activity
              className="
                h-8
                w-8
                text-blue-500
              "
            />

          </div>

        </div>

        <div className="
          rounded-xl
          border
          bg-white
          p-5
          shadow-sm
        ">

          <div className="
            flex
            items-center
            justify-between
          ">

            <div>

              <p className="
                text-sm
                text-zinc-500
              ">
                Average Latency
              </p>

              <h2 className="
                mt-2
                text-3xl
                font-bold
              ">
                {data.average_latency_ms} ms
              </h2>

            </div>

            <Clock3
              className="
                h-8
                w-8
                text-violet-500
              "
            />

          </div>

        </div>

        <div className="
          rounded-xl
          border
          bg-white
          p-5
          shadow-sm
        ">

          <div className="
            flex
            items-center
            justify-between
          ">

            <div>

              <p className="
                text-sm
                text-zinc-500
              ">
                Total Users
              </p>

              <h2 className="
                mt-2
                text-3xl
                font-bold
              ">
                {data.total_users}
              </h2>

            </div>

            <Users
              className="
                h-8
                w-8
                text-green-500
              "
            />

          </div>

        </div>

        <div className="
          rounded-xl
          border
          bg-white
          p-5
          shadow-sm
        ">

          <div className="
            flex
            items-center
            justify-between
          ">

            <div>

              <p className="
                text-sm
                text-zinc-500
              ">
                Total Models
              </p>

              <h2 className="
                mt-2
                text-3xl
                font-bold
              ">
                {data.total_models}
              </h2>

            </div>

            <Bot
              className="
                h-8
                w-8
                text-orange-500
              "
            />

          </div>

        </div>

        <div className="
          rounded-xl
          border
          bg-white
          p-5
          shadow-sm
        ">

          <div className="
            flex
            items-center
            justify-between
          ">

            <div>

              <p className="
                text-sm
                text-zinc-500
              ">
                API Keys
              </p>

              <h2 className="
                mt-2
                text-3xl
                font-bold
              ">
                {data.total_api_keys}
              </h2>

            </div>

            <KeyRound
              className="
                h-8
                w-8
                text-red-500
              "
            />

          </div>

        </div>

      </div>

      {/* Charts */}

      <AnalyticsCharts

        providers={
          data.providers
        }

        topModels={
          data.top_models
        }

      />

      {/* Top Users */}

      <div className="
        rounded-xl
        border
        bg-white
        shadow-sm
      ">

        <div className="
          border-b
          p-4
        ">

          <h2 className="
            font-semibold
          ">
            Top Users
          </h2>

        </div>

        <table className="w-full">

          <thead>

            <tr>

              <th className="
                p-4
                text-left
              ">
                User
              </th>

              <th className="
                p-4
                text-left
              ">
                Requests
              </th>

            </tr>

          </thead>

          <tbody>

            {
              data.top_users.map(
                (user) => (

                  <tr
                    key={
                      user.user_id
                    }
                    className="
                      border-t
                    "
                  >

                    <td className="
                      p-4
                    ">
                      User {user.user_id}
                    </td>

                    <td className="
                      p-4
                    ">
                      {user.requests}
                    </td>

                  </tr>
                )
              )
            }

          </tbody>

        </table>

      </div>

    </div>
  );
}