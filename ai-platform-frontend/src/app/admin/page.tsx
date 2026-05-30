import { StatCard } from "@/features/admin/components";

import {
  Users,
  MessageSquare,
  FileText,
  Activity,
  Bot,
  Cpu,
} from "lucide-react";

import { ProviderStatusCard } from "@/features/admin/components/provider-status-card";
import { WorkerStatusCard } from "@/features/admin/components/worker-status-card";
import { QueueStatusCard } from "@/features/admin/components/queue-status-card";

export default function AdminDashboardPage() {
  return (
    <div className="space-y-8">

      {/* Dashboard Header */}

      <div>
        <h1 className="text-3xl font-bold">
          Admin Dashboard
        </h1>

        <p className="text-sm text-zinc-500">
          AI Platform Administration Center
        </p>
      </div>

      {/* KPI Cards */}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">

        <StatCard
          title="Total Users"
          value={125}
          trend="+12%"
          icon={Users}
        />

        <StatCard
          title="Conversations"
          value={2450}
          trend="+8%"
          icon={MessageSquare}
        />

        <StatCard
          title="Documents"
          value={340}
          trend="+15%"
          icon={FileText}
        />

        <StatCard
          title="Requests"
          value={12000}
          trend="+25%"
          icon={Activity}
        />

        <StatCard
          title="Active Providers"
          value={5}
          trend="+2"
          icon={Bot}
        />

        <StatCard
          title="Active Workers"
          value={4}
          trend="100%"
          icon={Cpu}
        />

      </div>

      {/* Status Panels */}

      <div className="grid gap-6 lg:grid-cols-2">

        <ProviderStatusCard />

        <WorkerStatusCard />

      </div>

      <QueueStatusCard />

    </div>
  );
}