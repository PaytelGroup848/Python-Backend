"use client";

import {
  MessageSquare,
  Mic,
  FileText,
  ScanText,
  BarChart3,
  KeyRound,
  Settings,
  Sparkles,
  Bell,
  Search,
  LogOut,
  } from "lucide-react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/stores/auth-store";


interface DashboardLayoutProps {
  children: React.ReactNode;
}

const sidebarItems = [
  {
    title: "Chat",
    icon: MessageSquare,
  },
  {
    title: "Voice",
    icon: Mic,
  },
  {
    title: "Documents",
    icon: FileText,
  },
  {
    title: "OCR",
    icon: ScanText,
  },
  {
    title: "Analytics",
    icon: BarChart3,
  },
  {
    title: "API Keys",
    icon: KeyRound,
  },
  {
    title: "Settings",
    icon: Settings,
  },
];

export function DashboardLayout({
  children,
}: DashboardLayoutProps) {

    const router = useRouter();

  const logout =
    useAuthStore(
      (state) => state.logout
    );

  function handleLogout() {

    logout();

    localStorage.removeItem(
      "ai-platform-auth"
    );

    router.push("/login");
  }
  return (
    <div className="flex min-h-screen bg-black text-white">

      {/* Sidebar */}

      <aside
        className="
          hidden
          w-72
          border-r
          border-white/10
          bg-zinc-950
          lg:flex
          lg:flex-col
        "
      >
        {/* Logo */}

        <div
          className="
            flex
            items-center
            gap-3
            border-b
            border-white/10
            px-6
            py-6
          "
        >
          <div
            className="
              flex
              h-11
              w-11
              items-center
              justify-center
              rounded-2xl
              bg-white
              text-black
            "
          >
            <Sparkles className="h-5 w-5" />
          </div>

          <div>
            <h1 className="text-lg font-semibold">
              AI Platform
            </h1>

            <p className="text-xs text-zinc-400">
              Enterprise Infrastructure
            </p>
          </div>
        </div>

        {/* Navigation */}

        <nav className="flex-1 space-y-1 p-4">

          {sidebarItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.title}

               onClick={() =>
                 router.push(
                   item.title === "Chat"
                     ? "/chat"
                     : item.title === "Voice"
                     ? "/voice"
                     : item.title === "Documents"
                     ? "/documents"
                     : item.title === "OCR"
                     ? "/ocr"
                     : item.title === "Analytics"
                     ? "/analytics"
                     : item.title === "API Keys"
                     ? "/api-keys"
                     : "/settings"
                )
            }

            className="
              group
              flex
              w-full
              items-center
              gap-3
              rounded-2xl
              px-4
              py-3
              text-sm
              text-zinc-400
              transition-all
              hover:bg-white/5
              hover:text-white
            "
          >
           <Icon
             className="
               h-5
               w-5
               transition-transform
               group-hover:scale-110
            "
          />

        {item.title}
      </button>
    );
          })}
        </nav>

        {/* Bottom Section */}

        <div
          className="
            border-t
            border-white/10
            p-4
          "
        >
          <div
            className="
              rounded-2xl
              border
              border-white/10
              bg-zinc-900
              p-4
            "
          >
            <p className="text-sm font-medium">
              Enterprise Plan
            </p>

            <p className="mt-1 text-xs text-zinc-400">
              AI Infrastructure Workspace
            </p>

            <button
              onClick={handleLogout}
              className="
                mt-4
                flex
                w-full
                items-center
                justify-center
                gap-2
                rounded-xl
                border
                border-white/10
                bg-zinc-950
                px-4
                py-2
                text-sm
                text-zinc-300
                transition-all
                hover:bg-red-500/10
                hover:text-red-400
               "
            >
               <LogOut className="h-4 w-4" />

                Logout
              </button>
          </div>
        </div>
      </aside>

      {/* Main Section */}

      <div className="flex flex-1 flex-col">

        {/* Topbar */}

        <header
          className="
            sticky
            top-0
            z-50
            flex
            h-16
            items-center
            justify-between
            border-b
            border-white/10
            bg-black/80
            px-6
            backdrop-blur-xl
          "
        >
          {/* Search */}

          <div
            className="
              hidden
              items-center
              gap-3
              rounded-2xl
              border
              border-white/10
              bg-zinc-900
              px-4
              py-2
              md:flex
            "
          >
            <Search className="h-4 w-4 text-zinc-500" />

            <input
              placeholder="Search workspace..."
              className="
                bg-transparent
                text-sm
                text-white
                outline-none
                placeholder:text-zinc-500
              "
            />
          </div>

          {/* Right Side */}

          <div className="flex items-center gap-4">

            <button
              aria-label="Notifications"
              title="Notifications"
              className="
                flex
                h-10
                w-10
                items-center
                justify-center
                rounded-xl
                border
                border-white/10
                bg-zinc-900
                hover:bg-zinc-800
              "
            >
             <Bell className="h-4 w-4" />
            </button>

            <div
              className="
                h-10
                w-10
                rounded-full
                bg-gradient-to-br
                from-zinc-700
                to-zinc-900
              "
            />
          </div>
        </header>

        {/* Workspace */}

        <main className="flex-1 bg-black">
          {children}
        </main>
      </div>
    </div>
  );
}