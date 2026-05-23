"use client";

import {
  Moon,
  Sun,
} from "lucide-react";

import {
  useTheme,
} from "next-themes";

export function ThemeToggle() {

  const {
    theme,
    setTheme,
  } = useTheme();

  const isDark =
    theme === "dark";

  return (
    <button
      onClick={() =>
        setTheme(
          isDark
            ? "light"
            : "dark"
        )
      }

      className="
        flex
        h-10
        w-10
        items-center
        justify-center
        rounded-xl
        border
        border-black/10
        bg-white
        text-black
        transition-all
        hover:scale-105
        dark:border-white/10
        dark:bg-zinc-900
        dark:text-white
      "
    >
      {isDark ? (

        <Sun className="h-5 w-5" />

      ) : (

        <Moon className="h-5 w-5" />

      )}
    </button>
  );
}