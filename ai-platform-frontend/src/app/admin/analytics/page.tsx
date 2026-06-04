import {
  AnalyticsOverview
} from "@/features/admin/components/analytics-overview";

export default function Page() {

  return (

    <div className="space-y-6">

      <div>

        <h1 className="
          text-3xl
          font-bold
        ">
          Analytics
        </h1>

        <p className="
          text-zinc-500
        ">
          Platform analytics
        </p>

      </div>

      <AnalyticsOverview />

    </div>
  );
}