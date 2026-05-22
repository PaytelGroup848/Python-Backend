import { DashboardLayout }
  from "@/components/layout/dashboard-layout";

import { AuthGuard }
  from "@/components/auth/auth-guard";

import { ChatWindow }
  from "@/features/chat/components/chat-window";

import {
  ConversationSidebar,
} from "@/features/chat/components/conversation-sidebar";



export default function ChatPage() {

  return (
    <AuthGuard>

      <DashboardLayout>

        <div
          className="
            flex
            h-[calc(100vh-80px)]
            overflow-hidden
            rounded-3xl
            border
            border-white/10
            bg-zinc-950
          "
        >

          <ConversationSidebar />

          <div
            className="
              flex
              flex-1
              flex-col
              gap-4
              p-6
            "
          >

            

            <ChatWindow />

          </div>

        </div>

      </DashboardLayout>

    </AuthGuard>
  );
}