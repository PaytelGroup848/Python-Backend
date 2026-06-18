"use client";

import Link from "next/link";

import {
  usePathname,
  useRouter,
} from "next/navigation";

import {
  CreditCard,
} from "lucide-react";

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

import {
  LogOut,
} from "lucide-react";




import {
  useAuthStore,
} from "@/stores/auth-store";

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
      label: "Plans",
      href: "/admin/plans",
      icon: CreditCard,
    },
    {
      label: "Subscriptions",
      href: "/admin/subscriptions",
      icon: CreditCard,
    },
    {
      label: "Payments",
      href: "/admin/payments",
      icon: CreditCard,
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

  const pathname =
    usePathname();

  const router =
    useRouter();

  const user =
    useAuthStore(
      state => state.user
    );

  const logout =
    useAuthStore(
      state => state.logout
    );

  const handleLogout = () => {

    logout();

    router.replace(
      "/login"
    );
  };

  return (

    <aside
  className="
    flex
    h-screen
    w-72
    flex-col
    border-r
    bg-white
    p-4
  "
>

      <div className="mb-8">
        <h1 className="text-xl font-bold">
          AI Platform
        </h1>

        <p className="text-sm text-zinc-500">
          Admin Dashboard
        </p>
      </div>

      <nav className="space-y-6 flex-1">
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

      <div
  className="
    mt-auto
    border-t
    pt-4
  "
>

  <button
    onClick={handleLogout}
    className="
      flex
      w-full
      items-center
      justify-center
      gap-2
      rounded-lg
      bg-red-600
      px-4
      py-3
      text-white
      transition
      hover:bg-red-700
    "
  >

    <LogOut size={18} />

    Logout

  </button>

  <div
    className="
      mt-4
      flex
      items-center
      gap-3
      rounded-lg
      border
      p-3
    "
  >

    <div
      className="
        flex
        h-10
        w-10
        items-center
        justify-center
        rounded-full
        bg-zinc-800
        text-white
      "
    >

      {user?.email?.[0]?.toUpperCase() ?? "A"}

    </div>

    <div>

      <p className="text-sm font-medium">

        {user?.email ?? "Admin"}

      </p>

      <p
        className="
          text-xs
          text-zinc-500
        "
      >

        {user?.role ?? "admin"}

      </p>

    </div>

  </div>

</div>

    </aside>
  );
}