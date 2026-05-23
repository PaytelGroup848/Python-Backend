import { DashboardLayout } from "@/components/layout/dashboard-layout";

import { AuthGuard } from "@/components/auth/auth-guard";

export default function HomePage() {
  return (
    <AuthGuard>

      <DashboardLayout>

        <div className="mx-auto w-full max-w-7xl p-8">

          <div
            className="
              rounded-3xl
              border
              border-zinc-200
              bg-white
              p-8
              dark:border-white/10
              dark:bg-zinc-950
            "
          >
            <h1
              className="
                text-4xl
                font-semibold
                tracking-tight
                text-zinc-900
                dark:text-white
              "
            >
              Enterprise AI Platform
            </h1>

            <p
              className="
                mt-3
                max-w-2xl
                text-zinc-600
                dark:text-zinc-400
              "
            >
              Production-grade AI infrastructure platform
              with realtime voice, OCR pipelines,
              vector search, developer APIs,
              and scalable AI orchestration.
            </p>
          </div>

        </div>

      </DashboardLayout>

    </AuthGuard>
  );
}