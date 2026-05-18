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
        "
      >
        <h1 className="text-3xl font-semibold text-white">
          Welcome Back
        </h1>

        <p className="mt-2 text-zinc-400">
          Sign in to your AI workspace
        </p>

        <div className="mt-8">
          <LoginForm />
        </div>
      </div>
    </div>
  );
}