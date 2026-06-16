"use client";

import { StatCard } from "@/features/admin/components";

import {
  Users,
  UserCheck,
  CreditCard,
  Activity,
  Coins,
  Bot,
  Cpu,
  IndianRupee,
} from "lucide-react";

import {
  ProviderStatusCard,
} from "@/features/admin/components/provider-status-card";

import {
  WorkerStatusCard,
} from "@/features/admin/components/worker-status-card";

import {
  QueueStatusCard,
} from "@/features/admin/components/queue-status-card";

import {
  useDashboard,
} from "@/features/admin/hooks/use-dashboard";

export default function AdminDashboardPage() {

  const {
    data,
    isLoading,
    error,
  } = useDashboard();

  if (isLoading) {

    return (
      <div className="p-8">
        Loading Dashboard...
      </div>
    );
  }

  if (error) {

    return (
      <div className="p-8 text-red-500">
        Failed to load dashboard
      </div>
    );
  }

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

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

        <StatCard
          title="Total Users"
          value={data?.total_users ?? 0}
          trend="Live"
          icon={Users}
        />

        <StatCard
          title="Active Users"
          value={data?.active_users ?? 0}
          trend="Live"
          icon={UserCheck}
        />

        <StatCard
          title="Subscriptions"
          value={
            data?.active_subscriptions ?? 0
          }
          trend="Live"
          icon={CreditCard}
        />

        <StatCard
          title="API Requests"
          value={
            data?.total_requests ?? 0
          }
          trend="Live"
          icon={Activity}
        />

        <StatCard
          title="Tokens Used"
          value={
            (
              data?.total_tokens ?? 0
            ).toLocaleString()
          }
          trend="Live"
          icon={Coins}
        />

        <StatCard
          title="Revenue"
          value={`₹${
             data?.monthly_revenue ?? 0
          }`}
          trend="Live"
          icon={IndianRupee} 
        />

      <StatCard
        title="Active Providers"
        value={
          data?.active_providers ?? 0
        }
        trend="Live"
        icon={Bot}
      />

      <StatCard
        title="Active Workers"
        value={
          data?.active_workers ?? 0
        }
        trend="Live"
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