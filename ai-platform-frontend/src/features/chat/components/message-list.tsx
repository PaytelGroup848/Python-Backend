import ReactMarkdown
  from "react-markdown";

import remarkGfm
  from "remark-gfm";

import {
  Prism as SyntaxHighlighter,
} from "react-syntax-highlighter";

import {
  oneDark,
} from "react-syntax-highlighter/dist/esm/styles/prism";

import {
  ChatMessage,
} from "../types/chat.types";

import {
  useChatStore,
} from "../stores/chat-store";

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({
  messages,
}: MessageListProps) {

const isStreaming =
  useChatStore(
    (state) =>
      state.isStreaming
  );

  return (
    <div className="space-y-8">

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
              overflow-x-auto
              ${
                message.role ===
                "user"
                  ? `
                    bg-black
                    text-white
                    dark:bg-white
                    dark:text-black
                  `
                  : `
                    border
                    border-zinc-200
                    bg-white
                    text-zinc-900
                    dark:border-white/10
                    dark:bg-zinc-800
                    dark:text-white
                  `
              }
            `}
          >

<ReactMarkdown

  remarkPlugins={[
    remarkGfm
  ]}

  components={{

    code({
      className,
      children,
    }) {

      const match =
        /language-(\w+)/.exec(
          className || ""
        );

      return match ? (

        <SyntaxHighlighter
          style={oneDark}
          language={match[1]}
          PreTag="div"
        >
          {String(children).replace(
            /\n$/,
            ""
          )}
        </SyntaxHighlighter>

      ) : (

        <code
          className="
            rounded
            bg-zinc-200
            px-1.5
            py-1
            text-sm
            text-zinc-900
            dark:bg-zinc-900
            dark:text-white
          "
        >
          {children}
        </code>
      );
    },
  }}
>

  {message.content}

</ReactMarkdown>

{isStreaming &&
  message.id ===
    messages[
      messages.length - 1
    ]?.id && (

  <span
    className="
      ml-1
      animate-pulse
      text-zinc-500
      dark:text-zinc-400
    "
  >
    ▋
  </span>
)}

          </div>
        </div>
      ))}
    </div>
  );
}