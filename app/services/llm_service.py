

import asyncio

import time

import uuid

from app.modules.retrieval_runtime.services.rag_service import (
    retrieve_context
)


from app.services.conversation_service import save_conversation
from app.db.database import AsyncSessionLocal
from app.shared.cache.cache_service import (
    cache_service
)
from app.modules.memory.services.memory_service import (
    memory_service
)


from app.modules.providers.provider_registry import (
    provider_registry
)

from app.modules.usage.services.usage_tracker import (
    usage_tracker
)

# =========================
# ROUTES (ADD HERE)
# =========================

def route_query(query):
    query_lower = query.lower()

    if any(word in query_lower for word in ["code", "bug", "error", "debug", "fix"]):
        return "groq"

    elif any(word in query_lower for word in ["write", "story", "poem", "creative", "imagine"]):
        return "openai"

    elif any(word in query_lower for word in ["what", "why", "explain", "define", "concept"]):
        return "mistral"

    return "groq"



from app.modules.usage.services.usage_limit_service import (
    usage_limit_service
)

# =========================
#  MAIN ORCHESTRATOR
# =========================
async def get_fastest_response(
    query,
    user_id,
    user_department,
    user_role
):
    normalized_query = query.strip().lower()
    cache_key = f"{user_id}:{normalized_query}"

    request_id = str(
        uuid.uuid4()
    )

    print(
        f"REQUEST_ID={request_id}"
    )

    cached_data = await cache_service.get(
        cache_key
    )

    if cached_data:

        print("Cache hit")

        return cached_data
    print("Cache miss")

    # HARD LIMIT CHECK (ADD HERE)
    async with AsyncSessionLocal() as db:

        if not await usage_limit_service.check_usage_limit(
            db,
            user_id
        ):

            plan = await usage_limit_service.get_user_plan(
                db,
                user_id
            )

            return {
                "model": "system",
                "error_code": "PLAN_LIMIT_EXCEEDED",
                "response": (
                    f"You have reached the monthly "
                    f"usage limit for your "
                    f"{plan} subscription."
                )
            }
 

    #  RAG
    async with AsyncSessionLocal() as db:

       rag_result = await retrieve_context(
           db=db,
           query=query,
           user_department=user_department,
           user_role=user_role,
           top_k=3
        )

       context = rag_result["context"]

       sources = rag_result["sources"]

    #  Memory
    history = await memory_service.get_memory(
        user_id
    )

    messages = [
        {
            "role": "system",
            "content": """You are an enterprise AI assistant.

                          Use retrieved context when available.

                         If context is insufficient,
                         say you do not have enough information.

                         Avoid hallucinations."""
        }
    ]

# add previous conversation
    clean_history = []

    for msg in history:

        clean_history.append({

            "role": msg["role"],

            "content": msg["content"]
        })

    messages.extend(
        clean_history
    )

# add current query with context
    messages.append({
    "role": "user",
    "content": f"""Context:{context} Question:{query}"""})

    #  Smart routing
    model_choice = route_query(query)
    print(f" Routed to: {model_choice}")

    providers = [
        model_choice
    ]

    fallbacks = [
        "groq",
        "mistral",
        "openai",
        "gemini"
    ]

    for fallback in fallbacks:

        if fallback not in providers:

            providers.append(
                fallback
            )

    tried = set()

    result = None

    start_time = time.time()

    for provider in providers:

        if provider in tried:
           continue

        tried.add(provider)

        try:

           print(f"Trying provider: {provider}")

           provider_instance = (
                provider_registry[provider]
            )

           result = await provider_instance.generate(
                messages
            )
           
           result["provider"] = provider

           print(
                f"REQUEST_ID={request_id}"
            )

           print(
               f"PROVIDER_SUCCESS={provider}"
            )

           break

        except Exception as e:

            print(
                f"REQUEST_ID={request_id}"
            )

            print(
                f"PROVIDER_FAILED={provider}"
            )

            print(str(e))

            continue

    if result is None:

        return {
            "model": "system",
            "response": "All AI providers failed",
            "sources": sources
        }
    #  Cost tracking (ADD HERE)
    tokens = 0

    if isinstance(result, dict):

        usage = result.get(
            "usage",
            {}
        )

        prompt_tokens = usage.get(
            "prompt_tokens",
            0
        )

        completion_tokens = usage.get(
            "completion_tokens",
            0
        )

        tokens = usage.get(
            "total_tokens",
            0
        )
        print(
            "TRACKING:",
            {
                "provider": result.get("provider"),
                "model": result.get("model"),
                "tokens": tokens,
                "source": "chat"
            }
        )

        async with AsyncSessionLocal() as db:

            print(
                "BEFORE TRACK:",
                result.get("provider"),
                result.get("model"),
                tokens
            )

            print(
                f"REQUEST_ID={request_id}"
            )

            print(
                "TRACKING START"
            )

            await usage_tracker.track(

                db=db,

                user_id=user_id,

                api_key_id=None,

                model_name=result.get(
                    "model",
                    "unknown"
                ),

                provider=result.get(
                    "provider",
                    "unknown"
                ),

                source="chat",

                prompt_tokens=prompt_tokens,

                completion_tokens=completion_tokens,

                total_tokens=tokens,

                latency_ms=int(
                    (
                        time.time()
                        - start_time
                    ) * 1000
                )
            )

            print(
                f"REQUEST_ID={request_id}"
            )

            print("AFTER TRACK")

            # Future wallet deduction

            # await credit_deduction_service.deduct(
            #     user_id=user_id,
            #     model_name=result.get("model"),
            #     prompt_tokens=prompt_tokens,
            #     completion_tokens=completion_tokens
            # )


    await usage_limit_service.track_usage(

        user_id,

        tokens,
    )

    if isinstance(result, dict):
        await memory_service.save_memory(

            user_id,

            "user",

            query,
        )

        await memory_service.save_memory(

            user_id,

            "assistant",

            result["response"],
        )

    #  Save cache
    await cache_service.set(

        cache_key,

        result,

        ttl=300,
    )

    if isinstance(result, dict):

        print(
            f"REQUEST_ID={request_id}"
        )

        print(
            "FINAL RESPONSE FROM:",
            result.get("model")
        )

        try:

            await save_conversation(
                user_id=user_id,
                query=query,
                response=result["response"],
                model_used=result["model"]
            )

        except Exception as e:

            print(
                "Conversation save failed:"
            )

            print(str(e))

    return {
    "model": result.get("model"),
    "response": result.get("response"),
    "sources": sources
}

async def stream_response(text):

    words = text.split(" ")  

    for word in words:

        yield word + " "

        await asyncio.sleep(0.03)

