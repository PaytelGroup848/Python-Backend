import os
import httpx
import asyncio

import time
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
import numpy as np
from app.services.rag_service import retrieve_context
from app.db.redis_client import redis_client
from app.services.conversation_service import save_conversation
from app.db.database import AsyncSessionLocal

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY missing")

if not MISTRAL_API_KEY:
    print("WARNING: MISTRAL_API_KEY missing")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY missing")

##memory use if redis down
chat_memory = {}
#  Cache setup
cache = {}
CACHE_TTL = 60 * 5  # 5 minutes

#simple in-memory store

import json


MAX_HISTORY = 5

##token limit per day
MAX_TOKENS_PER_DAY = 10000

 ## cost tracking
COST_PER_1K_TOKENS = 0.002

##plan based limit

USER_PLANS = {
    "free": 10000,
    "pro": 100000,
    "enterprise": 1000000
}

#now currently store user normally in future upgarde and store in database 

USER_PLAN_MAP = {
    "user1": "free",
    "user2": "pro"
}


async def get_chat_history(user_id):

    data = await redis_client.get(user_id)

    if data:
        return json.loads(data)

    return []

async def update_chat_history(
    user_id,
    user_msg,
    bot_msg
):

    history = await get_chat_history(user_id)

    history.append({
        "role": "user",
        "content": user_msg
    })

    history.append({
        "role": "assistant",
        "content": bot_msg
    })

    await redis_client.setex(
        user_id,
        3600,
        json.dumps(history[-5:])
    )

#cost tracking and token according to users 

#def estimate_tokens(text):
 #   return int(len(text) / 4)


async def track_usage(
    user_id,
    tokens
):

    key = f"usage:{user_id}"

    current = await redis_client.get(key)

    current = int(current) if current else 0

    current += tokens

    await redis_client.setex(
        key,
        86400,
        current
    )

async def check_usage_limit(user_id):

    plan = USER_PLAN_MAP.get(user_id, "free")

    max_tokens = USER_PLANS[plan]

    key = f"usage:{user_id}"

    usage = await redis_client.get(key)

    if usage and int(usage) >= max_tokens:
        return False

    return True
# =========================
# SBERT MODEL
# =========================
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# ROUTES (ADD HERE)
# =========================
ROUTES = {
    "llama": "coding programming debugging errors software development",
    "mistral": "general knowledge explanation definition concept learning",
    "openai": "creative writing storytelling imagination conversation"
}

# =========================
# PRECOMPUTED EMBEDDINGS (ADD HERE)
# =========================
ROUTE_EMBEDDINGS = {
    model: embedding_model.encode(text)
    for model, text in ROUTES.items()
}

#routing based on the query

def route_query(query):
    query_lower = query.lower()

    if any(word in query_lower for word in ["code", "bug", "error", "debug", "fix"]):
        return "llama"

    elif any(word in query_lower for word in ["write", "story", "poem", "creative", "imagine"]):
        return "openai"

    elif any(word in query_lower for word in ["what", "why", "explain", "define", "concept"]):
        return "mistral"

    return "llama"


# =========================
#  SEMANTIC ROUTER (ADD HERE)
# =========================
def route_query_semantic(query):
    query_vec = embedding_model.encode(query)

    best_model = None
    best_score = -1

    for model, vec in ROUTE_EMBEDDINGS.items():   #  USE PRECOMPUTED
        score = np.dot(query_vec, vec) / (
            np.linalg.norm(query_vec) * np.linalg.norm(vec)
        )

        if score > best_score:
            best_score = score
            best_model = model

    return best_model

# =========================
#  OPENAI CALL
# =========================
async def call_openai(query):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}]
                }
            )

            data = response.json()
            print("OpenAI response:", data)

            if "choices" not in data:
                return {
                    "model": "openai",
                    "response": f"API Error: {data.get('error', 'Unknown error')}"
                }

            return {
                "model": "openai",
                "response": data["choices"][0]["message"]["content"]
            }

    except Exception as e:
        return {
            "model": "openai",
            "response": f"Exception: {str(e)}"
        }

async def call_mistral(query):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small",
                    "messages": [{"role": "user", "content": query}]
                }
            )

            data = response.json()
            print("Mistral response:", data)

            if "choices" not in data:
                return {
                    "model": "mistral",
                    "response": f"API Error: {data.get('error', 'Unknown error')}"
                }

            return {
                "model": "mistral",
                "response": data["choices"][0]["message"]["content"]
            }

    except Exception as e:
        return {
            "model": "mistral",
            "response": f"Exception: {str(e)}"
        }
    
async def call_llama(query):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": query}]
                }
            )

            data = response.json()
            print("Llama response:", data)

            if "choices" not in data:
                return {
                    "model": "llama",
                    "response": f"API Error: {data.get('error', 'Unknown error')}"
                }

            return {
                "model": "llama",
                "response": data["choices"][0]["message"]["content"]
            }

    except Exception as e:
        return {
            "model": "llama",
            "response": f"Exception: {str(e)}"
        }
# # =========================
# #  BACKUP MODEL (MOCK)
# # =========================
# async def call_backup_model(query):
#     await asyncio.sleep(2)
#     return "Backup response (second API)"

#memory and call

async def call_model_with_messages(
    messages,
    model_choice
):

    if (
        model_choice == "openai"
        and not OPENAI_API_KEY
    ):
        raise Exception(
            "OpenAI API key missing"
        )

    if (
        model_choice == "mistral"
        and not MISTRAL_API_KEY
    ):
        raise Exception(
            "Mistral API key missing"
        )

    if (
        model_choice == "llama"
        and not GROQ_API_KEY
    ):
        raise Exception(
            "Groq API key missing"
        )

    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:

        if model_choice == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            model = "gpt-4o-mini"

        elif model_choice == "mistral":
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            model = "mistral-small"

        else:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            model = "llama-3.1-8b-instant"

        response = await client.post(
            url,
            headers={**headers, "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "max_tokens": 150
}
            )

        data = response.json()

        if "choices" not in data:

            error_message = (
               data.get("error", {})
              .get("message", "Unknown API error")
            )

            raise Exception(error_message)

        return {
           "model": model_choice,
           "response": data["choices"][0]["message"]["content"],
           "usage": data.get("usage", {})
        }
# =========================
#  MAIN ORCHESTRATOR
# =========================
async def get_fastest_response(query, user_id="default"):
    normalized_query = query.strip().lower()
    cache_key = f"{user_id}:{normalized_query}"

    # HARD LIMIT CHECK (ADD HERE)
    if not await check_usage_limit(user_id):
       plan = USER_PLAN_MAP.get(user_id, "free")

       return {
            "model": "system",
            "response": f"Daily limit reached for {plan} plan. Upgrade to continue."
        }
    #  Cache check
    if cache_key in cache:
        cached_data = cache[cache_key]
        if time.time() - cached_data["time"] < CACHE_TTL:
            print(" Cache hit")
            return cached_data["response"]

    print(" Cache miss")

    

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
    history = await get_chat_history(user_id)

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
    model_choice = route_query_semantic(query)
    print(f" Routed to: {model_choice}")

    providers = []

    if model_choice == "openai" and OPENAI_API_KEY:
        providers.append("openai")

    if model_choice == "mistral" and MISTRAL_API_KEY:
        providers.append("mistral")

    if model_choice == "llama" and GROQ_API_KEY:
        providers.append("llama")

    if MISTRAL_API_KEY:
        providers.append("mistral")

    if GROQ_API_KEY:
       providers.append("llama")

    if OPENAI_API_KEY:
       providers.append("openai")

    tried = set()

    result = None

    for provider in providers:

        if provider in tried:
           continue

        tried.add(provider)

        try:

           print(f"Trying provider: {provider}")

           result = await call_model_with_messages(
               messages,
               provider
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

    await track_usage(
        user_id,
        tokens
    )

    if isinstance(result, dict):
        await update_chat_history(
           user_id,
           query,
           result["response"]
        )

    #  Save cache
    cache[cache_key] = {
        "response": result,
        "time": time.time()
    }

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
    
   
