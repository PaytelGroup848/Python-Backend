"use client";

import { useState } from "react";

import { useRouter } from "next/navigation";

import axios from "axios";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

import { authService } from "../services/auth.service";

import { useAuthStore } from "@/stores/auth-store";

export function LoginForm() {
  const router = useRouter();

  const setAuth = useAuthStore(
    (state) => state.setAuth
  );

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    try {
      setLoading(true);

      setError("");

      const response =
        await authService.login({
          email,
          password,
        });

      setAuth(
        response.user,
        response.access_token,
        response.refresh_token
      );

      router.push("/chat");

    } catch (err: unknown) {

      if (axios.isAxiosError(err)) {

        const detail =
          err.response?.data?.detail;

        if (Array.isArray(detail)) {

          setError(
            detail[0]?.msg ||
            "Login failed"
          );

        } else if (
          typeof detail === "string"
        ) {

          setError(detail);

        } else {

          setError("Login failed");
        }

      } else {

        setError(
          "Unexpected error occurred"
        );
      }

    } finally {

      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5"
    >
      {/* Error */}

      {error && (
        <div
          className="
            rounded-xl
            border
            border-red-500/20
            bg-red-500/10
            p-3
            text-sm
            text-red-400
          "
        >
          {error}
        </div>
      )}

      {/* Email */}

      <div className="space-y-2">
        <label className="text-sm text-zinc-300">
          Email
        </label>

        <Input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          className="
            border-white/10
            bg-zinc-900
            text-white
          "
        />
      </div>

      {/* Password */}

      <div className="space-y-2">
        <label className="text-sm text-zinc-300">
          Password
        </label>

        <Input
          type="password"
          placeholder="Enter your password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          className="
            border-white/10
            bg-zinc-900
            text-white
          "
        />
      </div>

      {/* Submit */}

      <Button
        type="submit"
        disabled={loading}
        className="
          w-full
          rounded-xl
        "
      >
        {loading
          ? "Signing In..."
          : "Sign In"}
      </Button>
    </form>
  );
}