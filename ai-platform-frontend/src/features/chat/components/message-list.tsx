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
              overflow-x-auto
              ${
                message.role ===
                "user"
                  ? `
                    bg-white
                    text-black
                  `
                  : `
                    border
                    border-white/10
                    bg-zinc-800
                    text-white
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
    ...props
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
          bg-zinc-900
          px-1.5
          py-1
          text-sm
        "
        {...props}
      >
        {children}
      </code>
    );
  },
}}
>

  {message.content}

</ReactMarkdown>

          </div>
        </div>
      ))}
    </div>
  );
}