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

    
    } catch (error: unknown) {

      if (error instanceof Error) {

        console.error(error.message);

      } else {

        console.error(error);

      }
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
        bg-zinc-100
        p-6
        dark:bg-black
      "
    >
      <div
        className="
          w-full
          max-w-md
          rounded-3xl
          border
          border-zinc-200
          bg-white
          p-8
          shadow-2xl
          dark:border-white/10
          dark:bg-zinc-950
        "
      >
        <h1
          className="
            text-3xl
            font-semibold
            text-zinc-900
            dark:text-white
          "
        >
          Create Account
        </h1>

        <p
          className="
            mt-2
            text-zinc-600
            dark:text-zinc-400
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
                text-zinc-800
                dark:text-white
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
                border-zinc-200
                bg-white
                px-4
                py-3
                text-zinc-900
                outline-none
                transition-all
                placeholder:text-zinc-500
                focus:border-zinc-400
                dark:border-white/10
                dark:bg-zinc-900
                dark:text-white
                dark:placeholder:text-zinc-400
                dark:focus:border-white/30
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
                text-zinc-800
                dark:text-white
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
                border-zinc-200
                bg-white
                px-4
                py-3
                text-zinc-900
                outline-none
                transition-all
                placeholder:text-zinc-500
                focus:border-zinc-400
                dark:border-white/10
                dark:bg-zinc-900
                dark:text-white
                dark:placeholder:text-zinc-400
                dark:focus:border-white/30
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
                text-zinc-800
                dark:text-white
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
                border-zinc-200
                bg-white
                px-4
                py-3
                text-zinc-900
                outline-none
                transition-all
                placeholder:text-zinc-500
                focus:border-zinc-400
                dark:border-white/10
                dark:bg-zinc-900
                dark:text-white
                dark:placeholder:text-zinc-400
                dark:focus:border-white/30
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
              bg-black
              py-3
              text-sm
              font-medium
              text-white
              transition-all
              hover:scale-[1.02]
              disabled:opacity-50
              dark:bg-white
              dark:text-black
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
            text-zinc-600
            dark:text-zinc-400
          "
        >
          Already have an account?{" "}

          <a
            href="/login"

            className="
              font-medium
              text-zinc-900
              hover:text-zinc-700
              dark:text-white
              dark:hover:text-zinc-300
            "
          >
            Sign In
          </a>
        </div>
      </div>
    </div>
  );
}
         