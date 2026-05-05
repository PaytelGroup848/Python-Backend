from fastapi import FastAPI, Request
from pydantic import BaseModel
from app.services.llm_service import get_fastest_response

#  Rate limiting imports
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

app = FastAPI()

#  Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


#  Handle rate limit errors
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please slow down."}
    )


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"


@app.get("/")
def home():
    return {"message": "AI LLM System Running"}


#  Apply rate limit here
@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest):
    response = await get_fastest_response(req.message, req.user_id)
    return response