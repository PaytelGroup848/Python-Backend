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
  PanelLeftClose,
  PanelLeftOpen,

  } from "lucide-react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/stores/auth-store";

import {
  ThemeToggle,
} from "@/components/theme/theme-toggle";
import { useState } from "react";


interface DashboardLayoutProps {
  children: React.ReactNode;
}

const sidebarItems = [
  {
    title: "Chat",
    icon: MessageSquare,
  },
  // {
  //   title: "Voice",
  //   icon: Mic,
  // },
  // {
  //   title: "Documents",
  //   icon: FileText,
  // },
  {
    title: "OCR",
    icon: ScanText,
  },
  {
    title: "Analytics",
    icon: BarChart3,
  },
  // {
  //   title: "API Keys",
  //   icon: KeyRound,
  // },
  {
    title: "Settings",
    icon: Settings,
  },
];

export function DashboardLayout({
  children,
}: DashboardLayoutProps) {

    const router = useRouter();
    const [isCollapsed, setIsCollapsed] = useState(false);

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
    <div
      className="
        flex
        min-h-screen
        bg-white
        text-black
        dark:bg-black
        dark:text-white
      "
    >

      {/* Sidebar */}

     <aside
  className={`
    hidden
    border-r
    border-zinc-200 dark:border-white/10
    bg-white dark:bg-zinc-950
    lg:flex
    lg:flex-col
    transition-all duration-300 ease-in-out
    ${isCollapsed ? "w-16" : "w-72"}
  `}
>
  {/* Logo */}

  <div
    className="
      flex
      items-center
      gap-3
      border-b
      border-zinc-200 dark:border-white/10
      px-4
      py-6
      justify-between
    "
  >
    <div className="flex items-center gap-3 overflow-hidden">
      <img
        className="
          flex
          h-11
          w-11
          shrink-0
          items-center
          justify-center
          rounded-2xl
          bg-white
          text-black
        "
        src="./Cloudedatalogo.svg"
      />

      {!isCollapsed && (
        <div className="whitespace-nowrap">
          <h1 className="text-lg font-semibold">
            AI Platform
          </h1>

          <p className="text-xs text-zinc-400">
            By CloudeData
          </p>
        </div>
      )}
    </div>

    <button
      type="button"
      aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      onClick={() => setIsCollapsed((prev) => !prev)}
      className="
        shrink-0
        flex h-8 w-8 items-center justify-center rounded-lg
        text-zinc-500
        transition hover:bg-zinc-100 hover:text-zinc-800
        dark:hover:bg-white/10 dark:hover:text-white
      "
    >
      {isCollapsed ? (
        <PanelLeftOpen className="h-5 w-5 mr-3" />
      ) : (
        <PanelLeftClose className="h-5 w-5" />
      )}
    </button>
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
                : item.title === "OCR"
                ? "/ocr"
                : item.title === "Analytics"
                ? "/analytics"
                : "/settings"
            )
          }

          title={isCollapsed ? item.title : undefined}

          className={`
            group
            flex
            w-full
            items-center
            gap-3
            rounded-2xl
            px-4
            py-3
            text-sm
            text-zinc-600
            transition-all
            hover:bg-zinc-200
            hover:text-black
            dark:text-zinc-400
            dark:hover:bg-white/5
            dark:hover:text-white
            ${isCollapsed ? "justify-center px-0" : ""}
          `}
        >
          <Icon
            className="
              h-5
              w-5
              shrink-0
              transition-transform
              group-hover:scale-110
            "
          />

          {!isCollapsed && item.title}
        </button>
      );
    })}
  </nav>

  {/* Bottom Section */}

  <div
    className="
      border-t
      border-zinc-200 dark:border-white/10
      p-4
    "
  >
    <div
      className={`
        rounded-2xl
        border
        border-zinc-200 dark:border-white/10
        bg-white dark:bg-zinc-900
        ${isCollapsed ? "p-2" : "p-4"}
      `}
    >
      {!isCollapsed && (
        <>
          <p className="text-sm font-medium">
            Enterprise Plan
          </p>

          <p
            className="
              mt-1
              text-xs
              text-zinc-600
              dark:text-zinc-400
            "
          >
            AI Infrastructure By CloudeData
          </p>
        </>
      )}

      <button
        onClick={handleLogout}
        title={isCollapsed ? "Logout" : undefined}
        className={`
          ${isCollapsed ? "" : "mt-4"}
          flex
          w-full
          items-center
          cursor-pointer
          justify-center
          gap-2
          rounded-xl
          border
          border-zinc-200
          bg-red-100
          px-4
          py-2
          text-sm
          text-red-700
          transition-all
          hover:bg-red-500/10
          hover:text-red-400
          dark:border-white/10
          dark:bg-zinc-950
          dark:text-zinc-300
        `}
      >
        <LogOut className="h-4 w-4 shrink-0" />

        {!isCollapsed && "Logout"}
      </button>
    </div>
  </div>
</aside>

      {/* Main Section */}

      <div className="flex flex-1 flex-col">

        {/* Topbar */}

        {/* <header
          className="
            sticky
            top-0
            z-50
            flex
            h-16
            items-center
            justify-between
            border-b
            border-zinc-200 dark:border-white/10
            bg-white/80 dark:bg-black/80
            px-6
            backdrop-blur-xl
          "
        >
\
          <div
            className="
              hidden
              items-center
              gap-3
              rounded-2xl
              border
              border-zinc-200 dark:border-white/10
              bg-zinc-100 dark:bg-zinc-900
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
                text-black dark:text-white
                outline-none
                placeholder:text-zinc-500
              "
            />
          </div>


          <div className="flex items-center gap-4">

            <ThemeToggle />

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
                border-zinc-200
                bg-white
                text-black
                transition-all
                hover:bg-zinc-100
                dark:border-white/10
                dark:bg-zinc-900
                dark:text-white
                dark:hover:bg-zinc-800
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
        </header> */}

        {/* Workspace */}

        <main
          className="
            flex-1
            bg-white
            dark:bg-black
          "
        >
          {children}
        </main>
      </div>
    </div>
  );
}