import asyncio
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
from sqlalchemy import text
from app.db.database import AsyncSessionLocal


from app.modules.auth.routes import (
    router as auth_router
)

#from app.routes.vector_routes import (
 #   router as vector_router
#)

from app.routes.pdf_routes import (
    router as pdf_router
)

#from app.routes.voice_routes import (
 #   router as voice_router
#)

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

#from app.routes.admin_routes import (
 #   router as admin_router
#)

from app.api.routes.metrics import (
    router as metrics_router
)
from app.api.routes.prometheus_routes import (
    router as prometheus_router
)
from app.modules.admin.routes.admin_routes import (
    router as admin_dashboard_router
)

from app.modules.api_keys.routes.api_key_routes import (
    router as api_key_router
)

from app.modules.public_api.routes.ai_api_routes import (
    router as public_api_router
)

from app.modules.media.routes.media_routes import (
    router as media_studio_router
)

from app.modules.models.routes.model_routes import (
    router as model_router
)

from app.modules.analytics.routes.analytics_routes import (
    router as analytics_router
)

from app.modules.usage.routes.usage_routes import (
    router as usage_router
)

from app.modules.billing.routes.billing_routes import (
    router as billing_router
)

from app.modules.pricing.routes.pricing_routes import (
    router as pricing_router
)

from app.jobs.scheduler import (
    scheduler
)

from app.modules.billing.routes.payment_routes import (
    router as payment_router
)
from app.modules.billing.routes.webhook_routes import (
    router as webhook_router
)

from app.modules.billing.routes.razorpay_webhook_routes import (
    router as razorpay_webhook_router
)

from app.modules.admin.routes.plan_admin_routes import (
    router as plan_admin_router
)

from app.modules.billing.routes.plan_routes import (
    router as public_plan_router
)

from app.modules.billing.routes.admin_subscription_routes import (
    router as admin_subscription_router
)

from app.modules.billing.routes.admin_payment_routes import (
    router as admin_payment_router
)

from app.modules.billing.routes.admin_invoice_routes import router as admin_invoice_router
from app.modules.billing.routes.subscription_routes import (
    router as subscription_router
)

from app.modules.billing.routes.invoice_download_routes import (
    router as invoice_download_router
)

from app.modules.billing.routes.company_settings_routes import (
    router as company_settings_router
)

from app.modules.knowledge_bases.routes.knowledge_base_document_routes import (
    router as knowledge_base_document_router
)

from app.modules.knowledge_bases.routes.knowledge_base_routes import (
    router as knowledge_base_router
)

from app.modules.assistants.routes.assistant_routes import (
    router as assistant_router
)

from app.modules.assistants.routes.assistant_knowledge_base_routes import (
    router as assistant_knowledge_base_router
)

from app.modules.training.routes.training_route import (
    router as training_router
)

from app.modules.training_providers.routes.training_provider_routes import (
    router as training_provider_router
)

from app.modules.corpora.routes.corpus_routes import (
    router as corpus_router
)

from app.modules.corpora.routes.corpus_source_routes import (
    router as corpus_source_router
)

from app.modules.ingestion.routes.ingestion_job_routes import (
    router as ingestion_router
)

from app.modules.connector_registry.routes.connector_type_route import (
    router as connector_type_router
)

from app.modules.connector_registry.routes.connector_implementation_route import (
    router as connector_implementation_router
)

from app.modules.connector_registry.routes.connector_instance_route import (
    router as connector_instance_router
)

from app.modules.dataset_records.routes.dataset_record_route import (
    router as dataset_record_router
)

from app.modules.data_pipelines.routes.data_pipeline_route import (
    router as data_pipeline_router
)

from app.modules.pipeline_runtime.routes.pipeline_runtime_route import (
    router as pipeline_runtime_router
)
from app.modules.pipeline_runtime.bootstrap.executor_bootstrap import (
    register_pipeline_executors,
)
from app.modules.dataset_builder.routes import (
    dataset_builder_router
)

from app.modules.datasets.routes.dataset_route import (
    router as dataset_router,
)

from app.modules.datasets.routes.dataset_upload_routes import (
    router as dataset_upload_router,
)

from app.modules.tokenizers.routes import (
    router as tokenizer_router,
)

from app.modules.storage_runtime.bootstrap.storage_runtime_bootstrap import (
    register_storage_runtime_factories,
)


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Mount media directory for generated images & persistent assets
import os
from fastapi.staticfiles import StaticFiles

media_root = os.path.join(os.getcwd(), "media")
os.makedirs(os.path.join(media_root, "generated", "images"), exist_ok=True)
app.mount("/media", StaticFiles(directory=media_root), name="media")

register_pipeline_executors()
# =========================
# CORS
# =========================

app.add_middleware(

    CORSMiddleware,

    
    allow_origins=[

        origin.strip()

        for origin in
        settings.ALLOWED_ORIGINS.split(",")

    ],



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
# Distributed Redis Pub/Sub WebSocket Listener (Singleton)
# =========================

_pubsub_listener_task: asyncio.Task | None = None


async def start_app_pubsub_listener():
    """
    Subscribes to pattern ws:req:* on Redis Pub/Sub.
    Routes real-time streaming chunks, stages, and completion events to
    the WebSocket connected to this application instance.
    Guarded to ensure exactly one listener runs per process.
    """
    import json
    from app.shared.redis.client import redis_client
    from app.shared.websocket.websocket_manager import websocket_manager

    logger.info("Initializing background Redis Pub/Sub WebSocket listener...")
    while True:
        pubsub = None
        try:
            pubsub = redis_client.pubsub()
            await pubsub.psubscribe("ws:req:*")
            logger.info("Redis Pub/Sub listener successfully subscribed to pattern 'ws:req:*'")

            async for message in pubsub.listen():
                if not message:
                    continue
                msg_type = message.get("type")
                if msg_type in ("pmessage", "message"):
                    channel = message.get("channel", "")
                    if isinstance(channel, bytes):
                        channel = channel.decode("utf-8")

                    # Channel format: ws:req:<request_id>
                    request_id = channel.replace("ws:req:", "")
                    data_raw = message.get("data")
                    if data_raw and request_id:
                        try:
                            if isinstance(data_raw, (bytes, bytearray)):
                                data = json.loads(data_raw.decode("utf-8"))
                            elif isinstance(data_raw, str):
                                data = json.loads(data_raw)
                            else:
                                data = data_raw

                            ws = websocket_manager.get_connection(request_id)
                            if ws:
                                await ws.send_json(data)

                            # Free request registry on completion
                            if isinstance(data, dict) and data.get("type") in ("done", "error", "stopped"):
                                websocket_manager.unregister_request(request_id)
                        except Exception as parse_err:
                            logger.warning(f"Error handling pubsub message for req {request_id}: {parse_err}")

        except asyncio.CancelledError:
            logger.info("Redis Pub/Sub listener task cancelled cleanly.")
            break
        except Exception as e:
            logger.error(f"Redis Pub/Sub listener connection lost: {e}. Reconnecting in 2s...")
            await asyncio.sleep(2)
        finally:
            if pubsub:
                try:
                    await pubsub.close()
                except Exception:
                    pass


async def start_app_response_listener():
    import asyncio, json
    from app.shared.redis.stream_service import redis_stream_service
    from app.shared.redis.client import redis_client
    from app.shared.constants.streams import CHAT_RESPONSE_STREAM
    from app.shared.websocket.websocket_manager import websocket_manager

    group_name = "app_response_listeners"
    consumer_name = "app_listener_1"

    while True:
        try:
            response = await redis_stream_service.consume(
                CHAT_RESPONSE_STREAM,
                group_name,
                consumer_name,
            )
            if not response:
                await asyncio.sleep(0.1)
                continue

            for stream in response:
                messages = stream[1]
                for message in messages:
                    message_id = message[0]
                    payload = message[1]
                    data = json.loads(payload.get("data", "{}"))
                    request_id = data.get("request_id")

                    websocket = websocket_manager.get_connection(request_id)
                    if websocket:
                        res_text = data.get("response") or data.get("content") or ""
                        conv_id = data.get("conversation_id")
                        try:
                            await websocket.send_json({"type": "start", "conversation_id": conv_id})
                            await websocket.send_json({"type": "chunk", "content": res_text, "response": res_text, "conversation_id": conv_id})
                            await websocket.send_json({"type": "done", "conversation_id": conv_id})
                        except Exception as e:
                            logger.warning(f"WS Send Error: {e}")

                    await redis_client.xack(
                        CHAT_RESPONSE_STREAM,
                        group_name,
                        message_id,
                    )
        except Exception as e:
            await asyncio.sleep(1)


@app.on_event("startup")
async def startup_event():
    global _pubsub_listener_task

    # 1. Verify database connectivity immediately on startup (fail-fast on misconfiguration)
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
    logger.info("Database connectivity verified on application startup.")

    register_storage_runtime_factories()

    register_pipeline_executors()

    scheduler.start()

    # Singleton spawn: Ensure exactly one listener task runs across the instance
    if _pubsub_listener_task is None or _pubsub_listener_task.done():
        _pubsub_listener_task = asyncio.create_task(start_app_pubsub_listener())

    asyncio.create_task(start_app_response_listener())
    from app.services.guest_refund_worker import start_guest_refund_worker_task
    start_guest_refund_worker_task(poll_interval=10.0)


@app.on_event("shutdown")
async def shutdown_event():
    global _pubsub_listener_task

    scheduler.shutdown()

    from app.services.guest_refund_worker import stop_guest_refund_worker_task
    await stop_guest_refund_worker_task()

    if _pubsub_listener_task and not _pubsub_listener_task.done():
        _pubsub_listener_task.cancel()
        try:
            await _pubsub_listener_task
        except asyncio.CancelledError:
            pass



# =========================
# Router Registration
# =========================

app.include_router(
    auth_router
)

#app.include_router(
 #   vector_router
#)

app.include_router(
    pdf_router
)

#app.include_router(
 #   voice_router
#)

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
    translation_router,
    prefix="/translate",
    tags=["Translation"]
)

#app.include_router(
 #   admin_router
#)

app.include_router(
    metrics_router
)

app.include_router(
    prometheus_router
)

app.include_router(
    admin_dashboard_router
)

app.include_router(
    api_key_router
)

app.include_router(
    public_api_router
)

app.include_router(
    media_studio_router
)

app.include_router(
    model_router
)

app.include_router(
    analytics_router
)

app.include_router(
    usage_router
)

app.include_router(
    billing_router
)

app.include_router(
    subscription_router
)

app.include_router(
    pricing_router
)

app.include_router(
    payment_router
)

app.include_router(
    webhook_router
)

app.include_router(
    razorpay_webhook_router
)

app.include_router(
    plan_admin_router
)

app.include_router(
    public_plan_router
)

app.include_router(
    admin_subscription_router
)

app.include_router(
    admin_payment_router
)

app.include_router(
    admin_invoice_router
)

app.include_router(
    invoice_download_router
)

app.include_router(
    company_settings_router
)

app.include_router(
    knowledge_base_router
)

app.include_router(
    knowledge_base_document_router
)

app.include_router(
    assistant_router
)

app.include_router(
    assistant_knowledge_base_router
)

app.include_router(
    training_router
)

app.include_router(
    training_provider_router
)

app.include_router(
    corpus_router
)

app.include_router(
    corpus_source_router
)

app.include_router(
    ingestion_router
)

app.include_router(
    connector_type_router
)

app.include_router(
    connector_implementation_router
)

app.include_router(
    connector_instance_router
)

app.include_router(
    dataset_record_router
)

app.include_router(
    dataset_upload_router
)

app.include_router(
    data_pipeline_router
)

app.include_router(
    pipeline_runtime_router
)   
app.include_router(
    dataset_builder_router
)

app.include_router(
    dataset_router
)

app.include_router(
    tokenizer_router,
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

