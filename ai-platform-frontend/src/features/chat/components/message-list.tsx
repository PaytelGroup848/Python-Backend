import {
  ChatMessage,
} from "../types/chat.types";

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({
  messages,
}: MessageListProps) {

  return (
    <div className="space-y-6">

      {messages.map((message) => (

        <div
          key={message.id}
          className={`
            flex
            ${
              message.role === "user"
                ? "justify-end"
                : "justify-start"
            }
          `}
        >
          <div
            className={`
              max-w-3xl
              rounded-2xl
              px-5
              py-4
              text-sm
              leading-7
              ${
                message.role ===
                "user"
                  ? "bg-white text-black"
                  : `
                    border
                    border-white/10
                    bg-zinc-800
                    text-white
                  `
              }
            `}
          >
            {message.content}
          </div>
        </div>
      ))}
    </div>
  );
}