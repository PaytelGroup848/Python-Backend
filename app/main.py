import uuid
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from app.services.llm_service import (
    get_fastest_response,
    stream_response
)
from app.services.agent_service import run_agent
from app.db.redis_client import redis_client
from app.core.security import verify_token
from app.core.config import settings

from app.services.audit_service import log_action  

 



import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.models import audit   
from app.models import conversation
from app.models import session



#  Rate limiting imports
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from app.modules.auth.routes import router as auth_router
from app.routes.vector_routes import router as vector_router
from app.db.database import Base, engine
from app.routes.pdf_routes import router as pdf_router
from app.routes.voice_routes import (
    router as voice_router
)

from app.modules.chat.routes.chat_ws_routes import (
    router as chat_ws_router
)

from sqlalchemy import select

from app.models.document import Document

from app.db.database import AsyncSessionLocal

from app.services.document_translation_service import (
    translate_large_text
)



app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#@app.on_event("startup")
#def startup():
 #   Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(vector_router)
app.include_router(pdf_router)
app.include_router(voice_router)
app.include_router(chat_ws_router)

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
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

##models(pydantic)
from typing import Optional

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class TranslationRequest(BaseModel):

    target_language: str
    

@app.get("/")
def home():
    return {"message": "AI LLM System Running"}

##
#  Apply rate limit here
@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, req: ChatRequest, user=Depends(verify_token)):

    user_id = user["user_id"]

    logger.info(f"User {user_id} sent chat request")

    if not req.session_id:
       req.session_id = str(uuid.uuid4())

    # Input validation
    if not req.message.strip():
        return {"error": "Empty message"}

    if len(req.message) > 1000:
        return {"error": "Message too long"}

    response = await get_fastest_response(req.message, user_id)
    try:
        log_action(user_id, "chat_request", "/chat")
    except Exception as e:
        logger.error(f"Audit log failed: {e}")  
    
    return {
       "session_id": req.session_id,
       "response": response
    }

@app.post("/agent-chat")

async def agent_chat(
    req: ChatRequest,
    user=Depends(verify_token)
):
    if not req.session_id:
       req.session_id = str(uuid.uuid4())

    response = await run_agent(
        query=req.message,
        session_id=req.session_id,
        user_id=user["user_id"],
        user_role=user["role"],
        user_department=user.get("department", "general")
    )

    return {
       "session_id": req.session_id,
       "response": response
    }

@app.post("/translate-document")
async def translate_document(
    req: TranslationRequest,
    user=Depends(verify_token)
):

    async with AsyncSessionLocal() as db:

        source_file = await redis_client.get(
            f"latest_pdf:{user['user_id']}"
        )

        if not source_file:

           return {
              "error": "No uploaded document found"
           }

        result = await db.execute(
            select(Document)
            .where(
               Document.source_file == source_file
            )
            .order_by(Document.page_number)
        )

        docs = result.scalars().all()

        if not docs:

            return {
                "error": "Document not found"
            }

        full_text = "\n\n".join([
            d.original_content or d.content
            for d in docs
        ])

        translated = translate_large_text(
            full_text,
            req.target_language
        )

        return {
            "source_file": source_file,
            "target_language": req.target_language,
            "translated_text": translated
        }

@app.post("/chat-stream")
@limiter.limit("10/minute")
async def chat_stream(
    request: Request,
    req: ChatRequest,
    user=Depends(verify_token)
):

    user_id = user["user_id"]

    result = await get_fastest_response(
        req.message,
        user_id
    )

    return StreamingResponse(
        stream_response(result["response"]),
        media_type="text/plain"
    )
##user token and cost
@app.get("/usage")
@limiter.limit("20/minute")
async def get_usage(request: Request, user=Depends(verify_token)):

    user_id = user["user_id"]   

    key = f"usage:{user_id}"

    usage = await redis_client.get(key)

    if not usage:
        return {"tokens": 0, "cost": 0}

    tokens = int(usage)

    cost = (tokens / 1000) * 0.002

    return {
        "tokens": tokens,
        "estimated_cost_usd": round(cost, 6)
    }

from app.core.security import require_role


#  Admin-only API
@app.get("/admin")
async def admin_only(user=Depends(require_role("admin"))):
    return {"message": "Admin access granted"}


#  Manager-only API
@app.get("/manager")
async def manager_only(user=Depends(require_role("manager"))):
    return {"message": "Manager access granted"}

from app.core.security import require_permission


@app.get("/admin-dashboard")
async def admin_dashboard(user=Depends(require_permission("view_admin_dashboard"))):
    try:
       log_action(user["user_id"], "view_admin_dashboard", "/admin-dashboard")
    except Exception as e:
       logger.error(f"Audit log failed: {e}")  
    return {"message": "Admin dashboard"}


@app.get("/reports")
async def reports(user=Depends(require_permission("view_reports"))):
    try:
       log_action(user["user_id"], "view_reports", "/reports")
    except Exception as e:
       logger.error(f"Audit log failed: {e}") 
    return {"message": "Reports data"}