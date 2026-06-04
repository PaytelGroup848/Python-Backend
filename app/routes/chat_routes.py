import uuid
import logging

from fastapi import (
    APIRouter,
    Depends,
    Request
)

from fastapi.responses import (
    StreamingResponse
)

from slowapi import Limiter

from app.core.security import (
    verify_token,
    require_role,
    require_permission
)

from app.services.llm_service import (
    get_fastest_response,
    stream_response
)

from app.services.agent_service import (
    run_agent
)

from app.db.redis_client import (
    redis_client
)

from app.services.audit_service import (
    log_action
)

from app.schemas.chat import (
    ChatRequest
)

logger = logging.getLogger(__name__)

router = APIRouter()

limiter = Limiter(
    key_func=lambda request:
    request.headers.get(
        "authorization",
        "anonymous"
    )
)


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    req: ChatRequest,
    user=Depends(verify_token)
):

    user_id = user["user_id"]

    logger.info(
        f"User {user_id} sent chat request"
    )

    if not req.session_id:

        req.session_id = str(
            uuid.uuid4()
        )

    if not req.message.strip():

        return {
            "error": "Empty message"
        }

    if len(req.message) > 1000:

        return {
            "error": "Message too long"
        }

    response = await get_fastest_response(
        req.message,
        user_id
    )

    try:

        log_action(
            user_id,
            "chat_request",
            "/chat"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {

        "session_id":
            req.session_id,

        "response":
            response
    }


@router.post("/agent-chat")
async def agent_chat(

    req: ChatRequest,

    user=Depends(
        verify_token
    )
):

    if not req.session_id:

        req.session_id = str(
            uuid.uuid4()
        )

    response = await run_agent(

        query=req.message,

        session_id=req.session_id,

        user_id=user["user_id"],

        user_role=user["role"],

        user_department=user.get(
            "department",
            "general"
        )
    )

    return {

        "session_id":
            req.session_id,

        "response":
            response
    }


@router.post("/chat-stream")
@limiter.limit("10/minute")
async def chat_stream(

    request: Request,

    req: ChatRequest,

    user=Depends(
        verify_token
    )
):

    user_id = user["user_id"]

    result = await get_fastest_response(

        req.message,

        user_id
    )

    return StreamingResponse(

        stream_response(
            result["response"]
        ),

        media_type="text/plain"
    )

# Deprecated:
# Replaced by
# /usage/overview
# in app/modules/usage
@router.get(
    "/usage",
    deprecated=True
)
@limiter.limit("20/minute")
async def get_usage(

    request: Request,

    user=Depends(
        verify_token
    )
):

    user_id = user["user_id"]

    key = f"usage:{user_id}"

    usage = await redis_client.get(key)

    if not usage:

        return {
            "tokens": 0,
            "cost": 0
        }

    tokens = int(usage)

    cost = (
        tokens / 1000
    ) * 0.002

    return {

        "tokens": tokens,

        "estimated_cost_usd":
            round(cost, 6)
    }


@router.get("/admin")
async def admin_only(
    user=Depends(
        require_role("admin")
    )
):

    return {
        "message":
            "Admin access granted"
    }


@router.get("/manager")
async def manager_only(
    user=Depends(
        require_role("manager")
    )
):

    return {
        "message":
            "Manager access granted"
    }


@router.get("/admin-dashboard")
async def admin_dashboard(

    user=Depends(
        require_permission(
            "view_admin_dashboard"
        )
    )
):

    try:

        log_action(

            user["user_id"],

            "view_admin_dashboard",

            "/admin-dashboard"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
            "Admin dashboard"
    }


@router.get("/reports")
async def reports(

    user=Depends(
        require_permission(
            "view_reports"
        )
    )
):

    try:

        log_action(

            user["user_id"],

            "view_reports",

            "/reports"
        )

    except Exception as e:

        logger.error(
            f"Audit log failed: {e}"
        )

    return {
        "message":
            "Reports data"
    }