import { DashboardLayout } from "@/components/layout/dashboard-layout";

import { AuthGuard } from "@/components/auth/auth-guard";

import { ChatWindow }
  from "@/features/chat/components/chat-window";

export default function ChatPage() {

  return (
    <AuthGuard>

      <DashboardLayout>

        <div className="mx-auto w-full max-w-6xl p-8">

          <ChatWindow />

        </div>

      </DashboardLayout>

    </AuthGuard>
  );
}