

import asyncio



from app.services.rag_service import retrieve_context
from app.db.redis_client import (
    redis_client
)

from app.services.conversation_service import save_conversation
from app.db.database import AsyncSessionLocal
from app.shared.cache.cache_service import (
    cache_service
)
from app.services.memory_service import (
    memory_service
)


from app.modules.chat.providers.provider_registry import (
    provider_registry
)


##plan based limit


#now currently store user normally in future upgarde and store in database 



#cost tracking and token according to users 








# =========================
# ROUTES (ADD HERE)
# =========================



def route_query(query):
    query_lower = query.lower()

    if any(word in query_lower for word in ["code", "bug", "error", "debug", "fix"]):
        return "llama"

    elif any(word in query_lower for word in ["write", "story", "poem", "creative", "imagine"]):
        return "openai"

    elif any(word in query_lower for word in ["what", "why", "explain", "define", "concept"]):
        return "mistral"

    return "llama"



from app.modules.chat.services.usage_service import (
    usage_service
)

# =========================
#  MAIN ORCHESTRATOR
# =========================
async def get_fastest_response(query, user_id="default"):
    normalized_query = query.strip().lower()
    cache_key = f"{user_id}:{normalized_query}"

    # HARD LIMIT CHECK (ADD HERE)
    if not await usage_service.check_usage_limit(
       user_id
    ):
       plan = await usage_service.get_user_plan(
            user_id
        )

       return {
            "model": "system",
            "response": f"Daily limit reached for {plan} plan. Upgrade to continue."
        }
    #  Cache check
    cached_data = await cache_service.get(
        cache_key
    )

    if cached_data:

        print("Cache hit")

        return cached_data

    print("Cache miss")

    

    #  RAG
    async with AsyncSessionLocal() as db:

       rag_result = await retrieve_context(
           db=db,
           query=query,
           user_department="general",
           user_role="employee",
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
    messages.extend(history)

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
        "llama",
        "mistral",
        "openai",
    ]

    for fallback in fallbacks:

        if fallback not in providers:

            providers.append(
                fallback
            )

    tried = set()

    result = None

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

           print(f"Success: {provider}")

           break

        except Exception as e:

            print(f"Provider failed: {provider}")
            print(str(e))

            continue

    if result is None:

       result = {
          "model": "system",
          "response": "All AI providers failed"
       }

    #  Cost tracking (ADD HERE)
    tokens = 0

    if isinstance(result, dict):

        usage = result.get(
            "usage",
            {}
        )

        tokens = usage.get(
            "total_tokens",
            0
        )

    await usage_service.track_usage(

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
            " Final response from:",
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

