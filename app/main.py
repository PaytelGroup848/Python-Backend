from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from app.services.llm_service import get_fastest_response
from app.db.redis_client import redis_client
from app.core.security import verify_token

#  Rate limiting imports
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.routes.auth import router as auth_router
from app.db.database import Base, engine

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth")

#  Initialize limiter
def get_user_key(request: Request):
    return request.headers.get("authorization", "anonymous")

limiter = Limiter(key_func=get_user_key)
app.state.limiter = limiter


#  Handle rate limit errors
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please slow down."}
    )

##middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

##models(pydantic)
class ChatRequest(BaseModel):
    message: str
    

@app.get("/")
def home():
    return {"message": "AI LLM System Running"}

##
#  Apply rate limit here
@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest, user=Depends(verify_token)):

    user_id = user["user_id"]

    # Input validation
    if not req.message.strip():
        return {"error": "Empty message"}

    if len(req.message) > 1000:
        return {"error": "Message too long"}

    response = await get_fastest_response(req.message, user_id)
    
    return response
##user token and cost
@app.get("/usage")
async def get_usage(user=Depends(verify_token)):

    user_id = user["user_id"]   #  ADD THIS

    key = f"usage:{user_id}"
    usage = redis_client.get(key)

    if not usage:
        return {"tokens": 0, "cost": 0}

    tokens = int(usage)
    cost = (tokens / 1000) * 0.002

    return {
        "tokens": tokens,
        "estimated_cost_usd": round(cost, 6)
    }