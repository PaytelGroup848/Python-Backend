import os
from fastapi import Header, HTTPException

# Store multiple API keys (later from DB)
VALID_API_KEYS = {
    "sk_live_a8x92kLmPq21": "user1",
    "sk_live_a8x92kLmPq23": "user2"
}

async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return VALID_API_KEYS[x_api_key]   # returns user_id