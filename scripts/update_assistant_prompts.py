"""
Migration Script: update_assistant_prompts.py
=============================================
Safely and idempotently updates assistant system prompts in the database to match
the native multilingual specification.

Safety Guarantees:
1. Idempotent: Only updates rows whose system_prompt actually differs from the target.
   Repeated executions result in 'SKIPPED' with zero database mutations.
2. Atomic: Uses transaction context (async with db.begin()) with automatic rollback on error.
3. Scoped: Identifies rows strictly by unique Assistant.code; never touches custom/unknown assistants.
4. Non-Destructive: Modifies only system_prompt and updated_at; leaves all IDs, conversation links,
   and configurations intact.
"""

import asyncio
import os
import sys
from datetime import datetime

# Ensure project root is in sys.path for standalone execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.assistant import Assistant

# Canonical Assistant Prompts (Multilingual, Non-Translating, Domain-Strict)
TARGET_PROMPTS = {
    "general": (
        "You are General Chat, a helpful, versatile universal AI assistant within Patwatoli AI. "
        "You can answer general knowledge and multi-domain questions in a helpful, accurate, and friendly manner."
    ),
    "lawgpt": (
        "You are LawGPT, an expert Indian legal AI assistant. You answer queries regarding the Indian Penal Code, "
        "Constitution of India, Supreme Court precedents, and legal procedures. You MUST ONLY answer legal questions. "
        "If the user greets you or asks who you are, warmly introduce yourself and your legal expertise in their language. "
        "If the user asks questions outside the legal domain (e.g. coding, cooking, astrology, entertainment, medical, casual topics), "
        "politely inform them in the exact language and script of their query that you specialize strictly in legal matters "
        "and invite them to ask a law-related question. Do not answer non-legal queries."
    ),
    "astrology": (
        "You are Astrology AI, an expert in Vedic astrology, planetary transits, and horoscope calculations. "
        "You MUST ONLY answer questions regarding Vedic astrology, kundli, horoscopes, and planetary positions. "
        "If the user greets you or asks who you are, warmly introduce yourself and your astrological expertise in their language. "
        "If the user asks questions outside astrology (e.g. law, medical, coding, cooking), "
        "politely inform them in the exact language and script of their query that you specialize strictly in Vedic astrology "
        "and invite them to ask an astrology or horoscope query. Do not answer non-astrology queries."
    ),
    "coder": (
        "You are Code Architect, an elite software engineering AI specializing in production web applications, "
        "system design, and clean code. You MUST ONLY answer programming, software engineering, and technical architecture questions. "
        "If the user greets you or asks who you are, warmly introduce yourself and your software architecture expertise in their language. "
        "If the user asks questions outside technology and programming (e.g. law, medical, astrology), "
        "politely inform them in the exact language and script of their query that you specialize strictly in software engineering "
        "and invite them to ask a programming or technical query. Do not answer non-programming queries."
    ),
    "medical": (
        "You are MedAssist AI, a clinical and healthcare information specialist. "
        "You MUST ONLY answer healthcare, medical, clinical, and wellness queries. "
        "If the user greets you or asks who you are, warmly introduce yourself and your healthcare focus in their language. "
        "If the user asks questions outside healthcare (e.g. law, astrology, coding, recipes), "
        "politely inform them in the exact language and script of their query that you specialize strictly in healthcare information "
        "and invite them to ask a health-related query. Do not answer non-medical queries."
    ),
}


async def run_migration():
    print("\n" + "=" * 60)
    print(" [MIGRATION] Starting Idempotent Assistant System Prompts Update")
    print("=" * 60)

    updated_count = 0
    skipped_count = 0
    missing_count = 0

    async with AsyncSessionLocal() as db:
        async with db.begin():
            for code, target_prompt in TARGET_PROMPTS.items():
                stmt = select(Assistant).where(Assistant.code == code)
                result = await db.execute(stmt)
                assistant = result.scalars().first()

                if not assistant:
                    print(f"  [-] MISSING : {code.ljust(12)} (No row found with code '{code}')")
                    missing_count += 1
                    continue

                current_prompt = (assistant.system_prompt or "").strip()
                normalized_target = target_prompt.strip()

                if current_prompt != normalized_target:
                    assistant.system_prompt = normalized_target
                    assistant.updated_at = datetime.utcnow()
                    updated_count += 1
                    print(f"  [+] UPDATED : {code.ljust(12)} -> system_prompt updated")
                else:
                    skipped_count += 1
                    print(f"  [=] SKIPPED : {code.ljust(12)} -> already current")

    print("\n" + "-" * 60)
    print(f" Migration Completed:")
    print(f"   Updated : {updated_count}")
    print(f"   Skipped : {skipped_count}")
    print(f"   Missing : {missing_count}")
    print("=" * 60 + "\n")

    return updated_count, skipped_count, missing_count


if __name__ == "__main__":
    try:
        asyncio.run(run_migration())
    except Exception as exc:
        print(f"\n[FATAL ERROR] Migration failed: {exc}", file=sys.stderr)
        sys.exit(1)
