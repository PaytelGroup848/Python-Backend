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
        
        >

          {/* <ConversationSidebar /> */}

          

            

            <ChatWindow />


        </div>

      </DashboardLayout>

    </AuthGuard>
  );
}