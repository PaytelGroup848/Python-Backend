import asyncio
import uuid

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from jose import jwt
from jose import JWTError

from app.db.database import (
    AsyncSessionLocal,
)

from app.models.message import (
    Message,
)

from app.models.conversation_session import (
    ConversationSession,
)

from app.shared.redis.stream_service import (
    redis_stream_service
)

from app.modules.chat.schemas.chat_event import (
    ChatEvent
)

from app.shared.websocket.websocket_manager import websocket_manager
print(
    "CHAT EVENT MODEL:",
    ChatEvent.model_json_schema()
)

from app.shared.constants.streams import (

    CHAT_REQUEST_STREAM,
)


from app.core.queues.queue_service import (
    queue_service
)


from app.core.logger import (
    logger,
)

from app.services.rate_limit_service import (
    check_rate_limit,
)

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket
):

    request_id = None

    # =========================
    # GET TOKEN
    # =========================

    token = websocket.query_params.get(
        "token"
    )

    if not token:
        logger.warning("WebSocket authentication rejected: Missing token")
        await websocket.close(code=1008)
        return

    # =========================
    # VERIFY TOKEN
    # =========================

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise JWTError("Missing sub claim")

        logger.info(
            f"Authenticated websocket user={user_id}"
        )

        await websocket.accept()
        await websocket_manager.connect(user_id, websocket)

        logger.info(
            "WebSocket connection accepted"
        )

    except JWTError as e:
        logger.warning(
            f"WebSocket JWT verification failed: {type(e).__name__}"
        )
        await websocket.close(
            code=1008
        )
        return

    # =========================
    # CHAT LOOP
    # =========================

    message_queue = asyncio.Queue(
        maxsize=10
    )

    try:

        while True:

            data = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=180,
            )

            # =========================
            # BACKPRESSURE CONTROL
            # =========================

            if message_queue.full():

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Too many pending requests"
                })

                continue

            await message_queue.put(data)

            queued_data = (
                await message_queue.get()
            )

            # =========================
            # HEARTBEAT
            # =========================

            if (
                queued_data.get("type")
                ==
                "ping"
            ):

                await websocket.send_json({

                    "type": "pong"
                })

                continue

            # =========================
            # STOP / CANCEL SIGNAL
            # =========================
            if (
                queued_data.get("type")
                ==
                "stop"
            ):
                stop_conv_id = queued_data.get("conversation_id")
                logger.info(
                    f"Stop generation signal received from user={user_id} conv={stop_conv_id}"
                )
                if stop_conv_id:
                    from app.shared.redis.client import redis_client
                    await redis_client.set(f"chat:stopped:{stop_conv_id}", "1", ex=60)

                await websocket.send_json({
                    "type": "stopped"
                })
                continue

            # =========================
            # VALIDATE MESSAGE
            # =========================

            message = queued_data.get(
                "message",
                ""
            )

            if not isinstance(
                message,
                str
            ):

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Invalid message format"
                })

                continue

            if not message.strip():

                continue

            if len(message) > 5000:

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Message too large"
                })

                continue

            conversation_id = (
                queued_data.get(
                    "conversation_id"
                )
            )

            assistant_id = (
                queued_data.get(
                    "assistant_id"
                )
            )

           

            if not conversation_id:

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Missing conversation_id"
                })

                continue

            logger.info(

                f"Message received "
                f"user={user_id} "
                f"conversation={conversation_id}"
            )

            # Store attached documents in Redis for this conversation
            attached_docs = queued_data.get("documents")
            if attached_docs and isinstance(attached_docs, list):
                try:
                    import json
                    from app.shared.redis.client import redis_client
                    await redis_client.set(f"conversation_pdf:{conversation_id}", json.dumps(attached_docs), ex=7200)
                    if len(attached_docs) > 0:
                        await redis_client.set(f"latest_pdf:{user_id}", str(attached_docs[0]), ex=7200)
                except Exception as _doc_err:
                    logger.warning(f"Failed to cache attached documents: {_doc_err}")

            # =========================
            # RATE LIMIT
            # =========================

            allowed = await check_rate_limit(
                str(user_id)
            )

            if not allowed:

                logger.warning(

                    f"Rate limit exceeded "
                    f"user={user_id}"
                )

                await websocket.send_json({

                    "type": "error",

                    "message":
                    "Rate limit exceeded"
                })

                continue

            # =========================
            # VALIDATE CONVERSATION
            # =========================

            async with AsyncSessionLocal() as db:

                conversation = await db.get(

                    ConversationSession,

                    conversation_id
                )

                if (
                    not conversation
                    or
                    conversation.user_id
                    !=
                    int(user_id)
                ):
                    logger.warning(
                        f"Conversation access mismatch: user={user_id} requested conv={conversation_id}"
                    )
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid conversation"
                    })
                    continue

                # =========================
                # SAVE USER MESSAGE
                # =========================

                try:

                    user_message = Message(

                        conversation_id=
                        conversation_id,

                        role="user",

                        content=message,
                    )

                    db.add(user_message)

                    await db.commit()

                except Exception:

                    await db.rollback()

                    raise

            # =========================
            # QUEUE REQUEST
            # =========================

            try:

                request_id = str(
                    uuid.uuid4()
                )

                
                websocket_manager.register_request(
                    request_id,
                    websocket
                )



               
                event = ChatEvent(

                    request_id=request_id,

                    user_id=user_id,

                    conversation_id=conversation_id,

                    assistant_id=assistant_id,

                    message=data.get("message"),

                    aspect_ratio=data.get("aspect_ratio") or "1024x1024",
                    web_search=bool(data.get("web_search", False)),
                )



                allowed = await (
                    queue_service
                    .can_enqueue(
                        str(user_id)
                    )
                )

                if not allowed:

                    await websocket.send_json({

                        "type": "error",

                        "message":
                        "Too many pending requests"
                    })

                    continue

               

                await redis_stream_service.publish(

                    CHAT_REQUEST_STREAM,

                    event.model_dump(),
                )

                await queue_service.increment(
                    str(user_id)
                )

                await websocket.send_json({

                    "type": "queued",

                    "request_id":
                    request_id,
                })

                logger.info(

                    f"Chat request queued "
                    f"user={user_id} "
                    f"request_id={request_id}"
                )

            except WebSocketDisconnect:

                logger.info(

                    f"Streaming disconnected "
                    f"user={user_id}"
                )
            

    except asyncio.TimeoutError:

        logger.warning(

            f"WebSocket timeout "
            f"user={user_id}"
        )

        await websocket.close()

        return

    except WebSocketDisconnect:

        logger.info(

            f"Client disconnected "
            f"user={user_id}"
        )

    finally:
        await websocket_manager.disconnect(user_id, websocket)
        logger.info(
            f"Cleaned up WS connection for user={user_id}"
        )

