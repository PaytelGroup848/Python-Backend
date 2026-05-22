"use client";

import {
  useState,
} from "react";
import {
  forgotPassword,
} from "@/features/auth/services/forgot-password-service";

export default function ForgotPasswordPage() {

  const [email, setEmail] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  async function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    try {

      setLoading(true);

      // future API call here

      await forgotPassword(email);

      alert(
        "Password reset link sent"
      );

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);
    }
  }

  return (
    <div
      className="
        flex
        min-h-screen
        items-center
        justify-center
        bg-black
        p-6
      "
    >
      <div
        className="
          w-full
          max-w-md
          rounded-3xl
          border
          border-white/10
          bg-zinc-950
          p-8
          shadow-2xl
        "
      >
        <h1
          className="
            text-3xl
            font-semibold
            text-white
          "
        >
          Forgot Password
        </h1>

        <p
          className="
            mt-2
            text-zinc-400
          "
        >
          Enter your email to reset password
        </p>

        <form
          onSubmit={handleSubmit}
                    className="
            mt-8
            space-y-5
          "
        >
          {/* EMAIL */}

          <div>

            <label
              className="
                mb-2
                block
                text-sm
                text-white
              "
            >
              Email
            </label>

            <input
              type="email"

              value={email}

              onChange={(e) =>
                setEmail(
                  e.target.value
                )
              }

              placeholder="Enter your email"

              className="
                w-full
                rounded-xl
                border
                border-white/10
                bg-zinc-900
                px-4
                py-3
                text-white
                outline-none
                transition-all
                focus:border-white/30
              "
            />
          </div>

          {/* BUTTON */}

          <button
            type="submit"

            disabled={loading}

            className="
              w-full
              rounded-xl
              bg-white
              py-3
              text-sm
              font-medium
              text-black
              transition-all
              hover:scale-[1.02]
              disabled:opacity-50
            "
          >
            {loading
              ? "Sending..."
              : "Send Reset Link"}
          </button>
        </form>

        {/* LOGIN LINK */}

        <div
          className="
            mt-6
            text-center
            text-sm
            text-zinc-400
          "
        >
          Remember your password?{" "}

          <a
            href="/login"

            className="
              font-medium
              text-white
              hover:text-zinc-300
            "
          >
            Sign In
          </a>
        </div>
      </div>
    </div>
  );
}