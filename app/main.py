import logging

from fastapi import (
    FastAPI,
    Request
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import (
    JSONResponse
)

from slowapi import Limiter
from slowapi.errors import (
    RateLimitExceeded
)

from app.core.config import settings

from app.models import audit
from app.models import conversation
from app.models import session

from app.modules.auth.routes import (
    router as auth_router
)

from app.routes.vector_routes import (
    router as vector_router
)

from app.routes.pdf_routes import (
    router as pdf_router
)

from app.routes.voice_routes import (
    router as voice_router
)

from app.modules.chat.routes.chat_ws_routes import (
    router as chat_ws_router
)

from app.modules.voice.routes.voice_ws_routes import (
    router as voice_ws_router
)

from app.routes.conversation_routes import (
    router as conversation_router
)

from app.routes.chat_routes import (
    router as chat_router
)

from app.routes.translation_routes import (
    router as translation_router
)

from app.routes.admin_routes import (
    router as admin_router
)

from app.api.routes.metrics import (
    router as metrics_router
)
from app.api.routes.prometheus_routes import (
    router as prometheus_router
)

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================
# Rate Limiter
# =========================

def get_user_key(
    request: Request
):

    return request.headers.get(
        "authorization",
        "anonymous"
    )


limiter = Limiter(
    key_func=get_user_key
)

app.state.limiter = limiter


# =========================
# Exception Handlers
# =========================

@app.exception_handler(
    RateLimitExceeded
)
def rate_limit_handler(

    request: Request,

    exc: RateLimitExceeded
):

    return JSONResponse(

        status_code=429,

        content={
            "error":
            "Too many requests. "
            "Please slow down."
        }
    )


# =========================
# Security Middleware
# =========================

@app.middleware("http")
async def security_headers(

    request: Request,

    call_next
):

    response = await call_next(
        request
    )

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "X-XSS-Protection"
    ] = "1; mode=block"

    response.headers[
        "Strict-Transport-Security"
    ] = (
        "max-age=31536000; "
        "includeSubDomains"
    )

    return response


# =========================
# Router Registration
# =========================

app.include_router(
    auth_router
)

app.include_router(
    vector_router
)

app.include_router(
    pdf_router
)

app.include_router(
    voice_router
)

app.include_router(
    chat_ws_router
)

app.include_router(
    voice_ws_router
)

app.include_router(
    conversation_router
)

app.include_router(
    chat_router
)

app.include_router(
    translation_router
)

app.include_router(
    admin_router
)

app.include_router(
    metrics_router
)

app.include_router(
    prometheus_router
)


# =========================
# Health Route
# =========================

@app.get("/")
async def home():

    return {
        "message":
        "AI LLM System Running"
    }