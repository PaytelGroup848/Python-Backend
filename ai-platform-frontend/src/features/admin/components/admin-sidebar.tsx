"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  LayoutDashboard,
  Users,
  Bot,
  Cpu,
  Database,
  Package,
  FileText,
  Mic,
  ScanText,
  BarChart3,
  Activity,
  Settings,
} from "lucide-react";

const navigation = [
  {
    title: "MAIN",
    items: [
      {
        label: "Dashboard",
        href: "/admin",
        icon: LayoutDashboard,
      },
      {
        label: "Users",
        href: "/admin/users",
        icon: Users,
      },
    ],
  },

  {
    title: "OPERATIONS",
    items: [
      {
        label: "Providers",
        href: "/admin/providers",
        icon: Bot,
      },
      {
        label: "Models",
        href: "/admin/models",
        icon: Package,
      },
      {
        label: "Workers",
        href: "/admin/workers",
        icon: Cpu,
      },
      {
        label: "Queues",
        href: "/admin/queues",
        icon: Database,
      },
    ],
  },

  {
    title: "AI SERVICES",
    items: [
      {
        label: "Documents",
        href: "/admin/documents",
        icon: FileText,
      },
      {
        label: "OCR",
        href: "/admin/ocr",
        icon: ScanText,
      },
      {
        label: "Voice",
        href: "/admin/voice",
        icon: Mic,
      },
    ],
  },

  {
    title: "SYSTEM",
    items: [
      {
        label: "Analytics",
        href: "/admin/analytics",
        icon: BarChart3,
      },
      {
        label: "Monitoring",
        href: "/admin/monitoring",
        icon: Activity,
      },
      {
        label: "Settings",
        href: "/admin/settings",
        icon: Settings,
      },
    ],
  },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 border-r bg-white p-4">

      <div className="mb-8">
        <h1 className="text-xl font-bold">
          AI Platform
        </h1>

        <p className="text-sm text-zinc-500">
          Admin Dashboard
        </p>
      </div>

      <nav className="space-y-6">
        {navigation.map((section) => (
          <div key={section.title}>
            <p className="mb-2 text-xs font-semibold text-zinc-400">
              {section.title}
            </p>

            <div className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;

                const active =
                  pathname === item.href;

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`
                      flex items-center gap-3 rounded-lg px-3 py-2 transition
                      ${
                        active
                          ? "bg-black text-white"
                          : "hover:bg-zinc-100"
                      }
                    `}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

    </aside>
  );
}