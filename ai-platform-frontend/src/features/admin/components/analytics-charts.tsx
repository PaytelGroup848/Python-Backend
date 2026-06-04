"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from "recharts";

interface Props {

  providers: {
    provider: string;
    requests: number;
  }[];

  topModels: {
    model_name: string;
    requests: number;
  }[];
}

const COLORS = [

  "#2563eb",
  "#7c3aed",
  "#059669",
  "#ea580c",
  "#dc2626",
  "#0891b2",
  "#9333ea"
];

export function AnalyticsCharts({

  providers,

  topModels

}: Props) {

  return (

    <div className="
      grid
      gap-6
      md:grid-cols-2
    ">

      {/* Provider Usage */}

      <div className="
        rounded-xl
        border
        bg-white
        p-6
        shadow-sm
      ">

        <h2 className="
          mb-4
          text-lg
          font-semibold
        ">
          Provider Usage
        </h2>

        <div className="h-80">

          {
            providers.length === 0
              ? (

                <div className="
                  flex
                  h-full
                  items-center
                  justify-center
                  text-zinc-400
                ">
                  No provider data
                </div>
              )
              : (

                <ResponsiveContainer>

                  <PieChart>

                    <Pie

                      data={providers}

                      dataKey="requests"

                      nameKey="provider"

                      outerRadius={110}

                      innerRadius={50}

                      label
                    >

                      {
                        providers.map(
                          (_, index) => (

                            <Cell

                              key={index}

                              fill={
                                COLORS[
                                  index %
                                  COLORS.length
                                ]
                              }
                            />
                          )
                        )
                      }

                    </Pie>

                    <Tooltip />

                    <Legend />

                  </PieChart>

                </ResponsiveContainer>
              )
          }

        </div>

      </div>

      {/* Top Models */}

      <div className="
        rounded-xl
        border
        bg-white
        p-6
        shadow-sm
      ">

        <h2 className="
          mb-4
          text-lg
          font-semibold
        ">
          Top Models
        </h2>

        <div className="h-80">

          {
            topModels.length === 0
              ? (

                <div className="
                  flex
                  h-full
                  items-center
                  justify-center
                  text-zinc-400
                ">
                  No model usage data
                </div>
              )
              : (

                <ResponsiveContainer>

                  <BarChart
                    data={topModels}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="model_name"
                    />

                    <YAxis />

                    <Tooltip />

                    <Bar

                      dataKey="requests"

                      fill="#2563eb"

                      radius={[
                        8,
                        8,
                        0,
                        0
                      ]}
                    />

                  </BarChart>

                </ResponsiveContainer>
              )
          }

        </div>

      </div>

    </div>
  );
}