import { LoginForm } from "@/features/auth/components/login-form";

export default function LoginPage() {

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
        {/* HEADING */}

        <h1
          className="
            text-3xl
            font-semibold
            text-white
          "
        >
          Welcome Back
        </h1>

        <p
          className="
            mt-2
            text-zinc-400
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
            text-zinc-400
          "
        >
          Don't have an account?{" "}

          <a
            href="/register"
            className="
              font-medium
              text-white
              transition-colors
              hover:text-zinc-300
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
              text-zinc-500
              transition-colors
              hover:text-white
            "
          >
            Forgot Password?
          </a>
        </div>
      </div>
    </div>
  );
}