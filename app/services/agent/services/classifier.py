from __future__ import annotations

import logging
import re
from app.services.agent.schemas import IntentType

logger = logging.getLogger("enterprise_agent")


class IntentClassifierService:

    @staticmethod
    async def classify(query: str) -> IntentType:
        q = query.lower().strip()

        # 1. Image generation intent detection (typo-tolerant, flexible phrasing, Hindi/Hinglish)
        negative_image_phrases = [
            "draw a conclusion", "draw conclusions",
            "draw comparison", "draw comparisons",
            "draw inspiration", "draw from"
        ]
        if not any(neg in q for neg in negative_image_phrases):
            image_verb_noun_regex = (
                r"\b(gen[e]?r[a]?te|creat[e]?|make|draw|paint|render|produce|show\s+me|give\s+me)\b"
                r".{0,30}\b(image|images|picture|pictures|photo|photos|pic|pics|artwork|illustration|portrait|wallpaper|tasveer)\b"
            )
            image_direct_noun_regex = (
                r"\b(image|images|picture|pictures|photo|photos|pic|pics|artwork|illustration|tasveer)\s+(of|for|showing|depicting)\b"
            )
            image_direct_draw_regex = r"\b(draw|paint|sketch|illustrate)\s+(a|an|the|me\s+a|me\s+an)\b"
            hinglish_image_terms = [
                "tasveer banao", "photo banao", "image banao", "pic banao",
                "tasveer bana", "photo bana", "image bana", "pic bana",
                "tasveer banaye", "photo banaye", "image banaye",
                "tasveer chahiye", "photo chahiye", "image chahiye"
            ]

            if (
                re.search(image_verb_noun_regex, q)
                or re.search(image_direct_noun_regex, q)
                or re.search(image_direct_draw_regex, q)
                or any(t in q for t in hinglish_image_terms)
                or "--ar " in q
                or q.startswith("/imagine")
            ):
                return IntentType.IMAGE_GEN

            # Conversational Image Edit intent detection
            edit_patterns = [
                r"\b(edit|modify|tweak|alter|remix)\b.{0,25}\b(image|picture|photo|pic|artwork|tasveer)\b",
                r"\b(change|turn|make|replace)\b.{0,30}\b(color|colour|background|bg|outfit|hair|lighting|style|sky|car|clothes|shirt)\b",
                r"\b(add|put|insert)\b.{0,30}\b(to\s+(the\s+)?(image|picture|photo|pic|scene)|in\s+(the\s+)?(image|picture|photo|pic|scene))\b",
                r"\b(remove|delete|erase)\b.{0,30}\b(from\s+(the\s+)?(image|picture|photo|pic|scene)|background|bg)\b",
                r"\b(upscale|4k|super\s+resolution)\b",
            ]
            hinglish_edit_terms = [
                "color change", "colour change", "background change", "bg change",
                "image edit", "photo edit", "pic edit", "tasveer edit",
                "isme change karo", "isme add karo", "isme se hatao", "bg hatao", "background hatao",
                "4k banao", "upscale karo", "clear karo image"
            ]
            if (
                any(re.search(p, q) for p in edit_patterns)
                or any(t in q for t in hinglish_edit_terms)
            ):
                return IntentType.IMAGE_EDIT

        # 2. Analytics intent detection (whole-word / structural patterns)
        analytics_patterns = [
            r"\banalyze\s+(the\s+|this\s+)?(dataset|data|table|csv|metrics|statistics)\b",
            r"\b(system\s+stats|dashboard\s+metrics|platform\s+usage|user\s+metrics|system\s+analytics)\b",
            r"^(show\s+)?(analytics|stats|metrics|dashboard|usage)\b"
        ]
        if any(re.search(p, q) for p in analytics_patterns):
            return IntentType.ANALYTICS

        # 3. Real-time Financial & Stock Market intelligence detection
        try:
            from app.modules.finance.finance_service import finance_service
            if finance_service.is_finance_query(query):
                return IntentType.FINANCE
        except Exception as exc:
            logger.debug(f"Finance intent detection bypassed: {exc}")

        # 4. Explicit Web Search / Real-time live info detection
        web_search_explicit_terms = [
            "search the web", "search online", "search internet", "browse the web", "google this", "web search",
            "latest news", "current news", "recent news", "today's news",
            "latest updates", "recent developments", "current price", "today's price",
            "who won the", "match score", "current weather", "who is the current"
        ]
        web_search_patterns = [
            r"\b(search\s+(the\s+)?web|search\s+online|search\s+internet|google\s+this|browse\s+the\s+web)\b",
            r"\b(latest|current|recent|today's|today|yesterday|upcoming)\b.{0,30}\b(news|update|updates|version|release|price|score|weather|event|events|election|status)\b",
            r"\b(who\s+is\s+the\s+current|what\s+is\s+the\s+latest|what\s+is\s+the\s+current)\b",
            r"\b(weather|temperature)\s+(in|at|today|now)\b",
            r"\bfind\s+(today'?s|the\s+latest|current)\s+(weather|price|news|score|temperature)\b",
            r"^(\/search|search:|\?)\s*",
            r"\[web search\]",
            r"--search",
        ]
        if (
            any(t in q for t in web_search_explicit_terms)
            or any(re.search(p, q) for p in web_search_patterns)
        ):
            return IntentType.SEARCH

        # 5. Explicit Document / RAG intent (only when referring to an actual attached/uploaded doc)
        rag_patterns = [
            r"\b(summarize|explain|review|read|check)\s+(this|the|attached|uploaded)\s+(pdf|document|file|report|policy|contract)\b",
            r"\b(this|the|attached|uploaded|given)\s+(pdf|document|file)\s+(says?|states?|contains?|mentions?)\b",
            r"\b(in\s+this\s+|from\s+this\s+|according\s+to\s+this\s+)(pdf|document|doc|report|file)\b",
            r"\b(attached|uploaded)\s+(pdf|document|doc|report|policy|contract)\b",
        ]
        if any(re.search(p, q) for p in rag_patterns):
            return IntentType.RAG

        # 6. Multi-step Execution Planning intent (explicit workflow plans)
        multistep_patterns = [
            r"\b(generate|create|build|make|give\s+me)\s+(an?\s+)?(execution\s+plan|step[- ]by[- ]step\s+plan|action\s+plan|detailed\s+project\s+plan)\b",
            r"\bbreak\s+(this\s+)?down\s+into\s+execution\s+steps\b",
        ]
        if any(re.search(p, q) for p in multistep_patterns):
            return IntentType.MULTISTEP

        # Default: General Chat (explanations, coding, questions, comparisons, chat)
        return IntentType.GENERAL
