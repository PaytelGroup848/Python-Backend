import os
import httpx
import asyncio

import time
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
import numpy as np
from app.services.rag_service import retrieve_context
from app.db.redis_client import redis_client, REDIS_AVAILABLE
from app.services.conversation_service import save_conversation
from app.db.database import SessionLocal

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#  Safety check
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing in .env")

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


def get_chat_history(user_id):
    if REDIS_AVAILABLE:
        data = redis_client.get(user_id)
        if data:
            return json.loads(data)
        return []
    else:
        return chat_memory.get(user_id, [])

def update_chat_history(user_id, user_msg, bot_msg):
    if REDIS_AVAILABLE:
        history = get_chat_history(user_id)

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})

        redis_client.setex(user_id, 3600, json.dumps(history[-5:]))

    else:
        history = chat_memory.get(user_id, [])

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_msg})

        chat_memory[user_id] = history[-5:]

#cost tracking and token according to users 

def estimate_tokens(text):
    return int(len(text) / 4)


def track_usage(user_id, tokens):
    if REDIS_AVAILABLE:
        key = f"usage:{user_id}"

        current = redis_client.get(key)
        current = int(current) if current else 0

        current += tokens
        redis_client.setex(key, 86400, current)

    else:
        # fallback (optional simple memory)
        pass

def check_usage_limit(user_id):
    plan = USER_PLAN_MAP.get(user_id, "free")
    max_tokens = USER_PLANS[plan]

    if REDIS_AVAILABLE:
        key = f"usage:{user_id}"
        usage = redis_client.get(key)

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

async def call_model_with_messages(messages, model_choice):
    async with httpx.AsyncClient(timeout=10.0) as client:

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
            return {
                "model": model_choice,
                "response": str(data)
            }

        return {
            "model": model_choice,
            "response": data["choices"][0]["message"]["content"]
        }
# =========================
#  MAIN ORCHESTRATOR
# =========================
async def get_fastest_response(query, user_id="default"):
    normalized_query = query.strip().lower()
    cache_key = f"{user_id}:{normalized_query}"

    # HARD LIMIT CHECK (ADD HERE)
    if not check_usage_limit(user_id):
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
    db = SessionLocal()

    try:

       rag_result = retrieve_context(
           db=db,
           query=query,
           top_k=3
       )

       context = rag_result["context"]

       sources = rag_result["sources"]

    finally:
      db.close()

    #  Memory
    history = get_chat_history(user_id)

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

    try:
        result = await call_model_with_messages(messages, model_choice)

        #  Fallback if failed
        if (
            isinstance(result, dict) and 
            ("API Error" in result.get("response", "") or 
            "Exception" in result.get("response", ""))
        ):
           if model_choice != "mistral":
             print(" Fallback → Mistral")
             result = await call_model_with_messages(messages, "mistral")
           else:
            print(" Fallback → Llama")
            result = await call_model_with_messages(messages, "llama")

    except Exception as e:
        result = {
            "model": "system",
            "response": "All models failed"
        }

    #  Cost tracking (ADD HERE)
    if isinstance(result, dict):
       tokens = estimate_tokens(result["response"])
       track_usage(user_id, tokens)

    if isinstance(result, dict):
        update_chat_history(user_id, query, result["response"])

    #  Save cache
    cache[cache_key] = {
        "response": result,
        "time": time.time()
    }

    if isinstance(result, dict):
       print(" Final response from:", result.get("model"))

       save_conversation(
           user_id=user_id,
           query=query,
           response=result["response"],
           model_used=result["model"]
        )

    return {
    "model": result.get("model"),
    "response": result.get("response"),
    "sources": sources
}

async def stream_response(text):

    words = text.split()

    for word in words:

        yield word + " "

        await asyncio.sleep(0.03)
    
   
