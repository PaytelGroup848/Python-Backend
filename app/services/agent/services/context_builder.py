from __future__ import annotations

import json
import re

from app.services.agent.prompts import (
    BRAND_DIRECTIVE,
    CONVERSATIONAL_MEMORY_DIRECTIVE,
    GENERAL_CHAT_MASTER_PROMPT,
    GREETING_CONVERSATIONAL_DIRECTIVE,
    GREETING_OPENERS,
    build_language_directive,
    build_suggestions_directive,
)
from app.services.language_service import (
    detect_language_and_script,
    get_language_directive,
)

__all__ = [
    "ContextBuilderService",
    "GENERAL_CHAT_MASTER_PROMPT",
    "CONVERSATIONAL_MEMORY_DIRECTIVE",
    "is_conversational_memory_query",
]

_MEMORY_QUERY_PATTERNS = (
    r"\b(piche|pehle|earlier|previous|previously)\b.{0,35}\b(baat|kaha|bola|discuss|discussed|talked|chat|conversation|poocha|bolatha|pucha|discuss\s+kiya)\b",
    r"\b(what\s+did\s+we\s+discuss|what\s+were\s+we\s+talking\s+about|our\s+previous\s+chat|summarize\s+our\s+chat)\b",
    r"\b(what\s+did\s+i\s+(say|ask|tell)|what\s+did\s+you\s+(say|answer|tell))\b",
    r"\b(mera\s+naam|what\s+is\s+my\s+name|who\s+am\s+i|kya\s+naam\s+hai\s+mera|naam\s+kya\s+hai)\b",
    r"\b(remember\s+what|do\s+you\s+remember|kya\s+yaad\s+hai|yaad\s+hai\s+kuch)\b",
    r"\b(repeat\s+that|what\s+did\s+you\s+just\s+say|what\s+did\s+i\s+just\s+say)\b",
)

_BLOCKED_CONTEXT_PATTERNS = (
    r"ignore\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"bypass\s+security",
)


def is_conversational_memory_query(query: str) -> bool:
    """Detects if a query refers to preceding conversation turns, history, or user identity."""
    if not query or not isinstance(query, str):
        return False
    q = query.lower().strip()
    return any(re.search(pattern, q) for pattern in _MEMORY_QUERY_PATTERNS)


def _is_greeting_opener(query: str) -> bool:
    normalized = (query or "").strip().lower().rstrip("!.,? ")
    return normalized in GREETING_OPENERS


def _serialize_tool_result(tool_result: dict | None) -> str:
    if not tool_result or not isinstance(tool_result, dict):
        return ""
    return json.dumps(tool_result, ensure_ascii=False)


class ContextBuilderService:
    """Builds structured ChatML messages and budget-aware fallback prompts."""

    @staticmethod
    def parse_memory_to_messages(memory_text: str) -> list[dict[str, str]]:
        """Parses serialized role-prefixed memory lines into ChatML message turns."""
        if not memory_text or not isinstance(memory_text, str):
            return []

        parsed: list[dict[str, str]] = []
        current_role: str | None = None
        current_lines: list[str] = []

        def flush() -> None:
            if current_role and current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    parsed.append({"role": current_role, "content": content[:3000]})
                current_lines.clear()

        for line in memory_text.split("\n"):
            if line.startswith("user: "):
                flush()
                current_role = "user"
                current_lines.append(line[6:])
            elif line.startswith("assistant: "):
                flush()
                current_role = "assistant"
                current_lines.append(line[11:])
            elif current_role:
                current_lines.append(line)

        flush()
        return parsed

    @staticmethod
    def sanitize_context(context: str) -> str:
        """Strips known prompt-injection phrases from retrieved context."""
        if not context:
            return ""
        sanitized = str(context)
        for pattern in _BLOCKED_CONTEXT_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        return sanitized

    @staticmethod
    def _build_core_directives(query: str) -> tuple[str, str, bool]:
        """Returns (shared_directives_block, target_label, is_greeting) for the query."""
        detected_lang = detect_language_and_script(query)
        target_directive = get_language_directive(detected_lang)
        target_label = detected_lang.get("label", "English")

        shared = (
            f"{BRAND_DIRECTIVE}\n\n"
            f"{build_language_directive(target_directive)}\n\n"
            f"{GREETING_CONVERSATIONAL_DIRECTIVE}\n\n"
            f"{CONVERSATIONAL_MEMORY_DIRECTIVE}\n\n"
            f"{build_suggestions_directive(target_label)}"
        )
        return shared, target_label, _is_greeting_opener(query)

    @staticmethod
    def build_chat_messages(
        query: str,
        system_prompt: str = "",
        memory: str = "",
        context: str = "",
        tool_result: dict | None = None,
        plan: str = "",
        web_citation_instr: str = "",
        max_total_chars: int = 36000,
    ) -> list[dict[str, str]]:
        """Builds a ChatML message list for streaming/chat-capable LLM providers."""
        clean_ctx = ContextBuilderService.sanitize_context(context or "")
        tool_str = _serialize_tool_result(tool_result)
        shared_directives, target_label, is_greeting = ContextBuilderService._build_core_directives(query)

        role_prompt = (
            system_prompt.strip()
            if system_prompt and system_prompt.strip()
            else GENERAL_CHAT_MASTER_PROMPT
        )

        system_content = f"{role_prompt}\n\n{shared_directives}"
        if plan:
            system_content += f"\n\nExecution Plan:\n{plan[:1000]}"
        if tool_str:
            system_content += f"\n\nTool Results:\n{tool_str[:1000]}"

        messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]

        if clean_ctx:
            ctx_text = clean_ctx[:20000]
            if web_citation_instr:
                ctx_text = f"{web_citation_instr}\n\n{ctx_text}"
            messages.append({"role": "system", "content": f"RETRIEVED CONTEXT & REFERENCE MATERIAL:\n{ctx_text}"})

        if memory:
            history_turns = ContextBuilderService.parse_memory_to_messages(memory)
            if history_turns and history_turns[-1].get("role") == "user" and history_turns[-1].get("content", "").strip() == query.strip():
                history_turns = history_turns[:-1]
            messages.extend(history_turns[-10:])

        messages.append({
            "role": "system",
            "content": (
                f"REMINDER: End your response with **💡 Suggestions:** followed by 3-4 short bulleted follow-up questions in {target_label} (under 15 words each, no prefix labels)."
            ),
        })

        user_prompt = query
        if is_greeting:
            user_prompt += "\n\n(Reminder: This is a greeting opener. Greet warmly in 1-2 friendly sentences and provide 3-4 capability starter questions under **💡 Suggestions:**.)"

        messages.append({"role": "user", "content": user_prompt})
        return messages

    @staticmethod
    def build_prompt(
        query: str,
        system_prompt: str = "",
        memory: str = "",
        context: str = "",
        tool_result: dict | None = None,
        plan: str = "",
        web_citation_instr: str = "",
        max_total_chars: int = 36000,
    ) -> str:
        """Builds a budget-aware flat prompt string for batch/non-ChatML fallback providers."""
        clean_ctx = ContextBuilderService.sanitize_context(context or "")
        tool_str = _serialize_tool_result(tool_result)
        shared_directives, target_label, is_greeting = ContextBuilderService._build_core_directives(query)

        role_prompt = (
            system_prompt.strip()
            if system_prompt and system_prompt.strip()
            else "You are General Chat, a helpful, versatile universal AI assistant within Patwatoli AI."
        )
        system_section = f"{shared_directives}\n\nAssistant Role & Instructions:\n{role_prompt}"

        greeting_note = (
            "\nSPECIAL MANDATE FOR GREETING:\n"
            "The user sent a greeting. DO NOT define or explain the word 'hi'. "
            "Reply warmly and naturally in 1-2 friendly sentences offering your assistance, "
            "and provide 3-4 capability starter suggestions at the end.\n\n"
            if is_greeting
            else ""
        )

        user_section = (
            f"USER QUESTION:\n{query}\n\n"
            f"LANGUAGE DIRECTIVE REMINDER:\n"
            f"Respond strictly in {target_label} matching the USER QUESTION above unless the user explicitly requested a different language.\n\n"
            f"{greeting_note}"
            f"FOLLOW-UP SUGGESTIONS MANDATE:\n"
            f"At the very end of your response, you MUST provide 3 to 4 short, natural follow-up questions that the user might say next in {target_label} (matching your answer language).\n"
            f"Rules: Output ONLY the direct question on each bullet point without prefix labels like 'Suggestion:' or 'Follow-up:'.\n"
            f"Format strictly as:\n"
            f"**💡 Suggestions:**\n"
            f"- <Direct follow-up question>\n"
            f"- <Direct follow-up question>\n"
            f"- <Direct follow-up question>\n\n"
            f"ANSWER ({target_label.upper()}):\n"
        )
        if web_citation_instr:
            user_section = f"{web_citation_instr}\n\n{user_section}"

        budget_remaining = max(0, max_total_chars - len(system_section) - len(user_section) - 500)
        plan_str = plan[:1000] if plan else ""
        bounded_tool = tool_str[:1000] if tool_str else ""
        budget_remaining = max(0, budget_remaining - len(plan_str) - len(bounded_tool))

        safe_memory = memory[-4000:] if memory else ""
        if safe_memory:
            trimmed_mem = safe_memory.rstrip()
            user_trail = f"user: {query.strip()}"
            if trimmed_mem.endswith(user_trail):
                safe_memory = trimmed_mem[:-len(user_trail)].rstrip()
        budget_remaining = max(0, budget_remaining - len(safe_memory))

        if clean_ctx and len(clean_ctx) > budget_remaining:
            safe_context = clean_ctx[:budget_remaining] + "\n\n[... Remaining context omitted for budget ...]"
        else:
            safe_context = clean_ctx

        parts = [system_section]
        if plan_str:
            parts.append(f"Execution Plan:\n{plan_str}")
        if safe_memory:
            parts.append(f"Conversation Memory:\n{safe_memory}")
        if safe_context:
            parts.append(f"Retrieved Context:\n{safe_context}")
        if bounded_tool:
            parts.append(f"Tool Result:\n{bounded_tool}")
        parts.append(user_section)

        return "\n\n".join(parts)

    @staticmethod
    def build(
        system_prompt: str,
        memory: str,
        context: str,
        tool_result: dict,
        plan: str,
    ) -> str:
        """Backward-compatibility wrapper for legacy callers."""
        return ContextBuilderService.build_prompt(
            query="",
            system_prompt=system_prompt,
            memory=memory,
            context=context,
            tool_result=tool_result,
            plan=plan,
        )
