export interface ChatMessage {

  id: string | number;

  role:
    | "user"
    | "assistant";

  content: string;
}