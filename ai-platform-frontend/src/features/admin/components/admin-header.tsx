"use client";

import {
  Bell,
  Moon,
  Search,
  User,
} from "lucide-react";

export function AdminHeader() {
  return (
    <header
      className="
        flex
        h-16
        items-center
        justify-between
        border-b
        border-zinc-200
        bg-white
        px-6
      "
    >
      {/* Search */}

      <div className="relative w-96">

        <Search
          size={18}
          className="
            absolute
            left-3
            top-1/2
            -translate-y-1/2
            text-zinc-400
          "
        />

        <input
          placeholder="Search..."
          className="
            w-full
            rounded-lg
            border
            border-zinc-200
            py-2
            pl-10
            pr-4
            outline-none
          "
        />

      </div>

      {/* Right Side */}

      <div
        className="
          flex
          items-center
          gap-4
        "
      >

        <button
          className="
            rounded-lg
            p-2
            hover:bg-zinc-100
          "
        >
          <Bell size={20} />
        </button>

        <button
          className="
            rounded-lg
            p-2
            hover:bg-zinc-100
          "
        >
          <Moon size={20} />
        </button>

        <div
          className="
            flex
            items-center
            gap-2
            rounded-lg
            border
            border-zinc-200
            px-3
            py-2
          "
        >
          <User size={18} />

          <span className="text-sm">
            Admin
          </span>
        </div>

      </div>
    </header>
  );
}