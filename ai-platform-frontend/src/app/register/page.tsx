"use client";

import {
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import {
  registerUser,
} from "@/features/auth/services/register-service";

export default function RegisterPage() {

  const router =
    useRouter();

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  async function handleRegister(
    e: React.FormEvent
  ) {

    e.preventDefault();

    try {

      setLoading(true);

      await registerUser(
        name,
        email,
        password
      );

      router.push("/login");

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
          Create Account
        </h1>

        <p
          className="
            mt-2
            text-zinc-400
          "
        >
          Register for your AI workspace
        </p>

        <form
          onSubmit={handleRegister}
          className="
            mt-8
            space-y-5
          "
        >
          {/* NAME */}

          <div>

            <label
              className="
                mb-2
                block
                text-sm
                text-white
              "
            >
              Full Name
            </label>

            <input
              type="text"

              value={name}

              onChange={(e) =>
                setName(
                  e.target.value
                )
              }

              placeholder="Enter your full name"

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

          {/* PASSWORD */}

          <div>

            <label
              className="
                mb-2
                block
                text-sm
                text-white
              "
            >
              Password
            </label>

            <input
              type="password"

              value={password}

              onChange={(e) =>
                setPassword(
                  e.target.value
                )
              }

              placeholder="Create password"

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
              ? "Creating..."
              : "Create Account"}
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
          Already have an account?{" "}

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
         