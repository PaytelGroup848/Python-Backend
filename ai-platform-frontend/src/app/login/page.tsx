import { LoginForm } from "@/features/auth/components/login-form";

export default function LoginPage() {
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
        {/* HEADING */}

        <h1
          className="
            text-3xl
            font-semibold
            text-zinc-900 dark:text-white
          "
        >
          Welcome Back
        </h1>

        <p
          className="
            mt-2
            text-zinc-600 dark:text-zinc-400
          "
        >
          Sign in to your AI workspace
        </p>

        {/* LOGIN FORM */}

        <div className="mt-8">
          <LoginForm />
        </div>

        {/* REGISTER LINK */}

        <div
          className="
            mt-6
            text-center
            text-sm
            text-zinc-600 dark:text-zinc-400
          "
        >
          Don&apos;t have an account?{" "}

          <a
            href="/register"
            className="
              font-medium
              text-zinc-900
              transition-colors
              hover:text-zinc-700
              dark:text-white
              dark:hover:text-zinc-300
            "
          >
            Create Account
          </a>
        </div>

        {/* FORGOT PASSWORD */}

        <div className="mt-3 text-center">
          <a
            href="/forgot-password"
            className="
              text-sm
              text-zinc-600
              transition-colors
              hover:text-zinc-900
              dark:text-zinc-500
              dark:hover:text-white
            "
          >
            Forgot Password?
          </a>
        </div>
      </div>
    </div>
  );
}