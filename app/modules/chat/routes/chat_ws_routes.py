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

from app.shared.events.chat_event import (
    ChatEvent
)

from app.shared.constants.streams import (
    CHAT_REQUEST_STREAM
)

from app.modules.chat.services.ws_manager import (
    ws_manager
)

from app.modules.chat.services.queue_service import (
    queue_service
)

from app.shared.metrics.metrics_service import (
    metrics_service
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

        await websocket.send_json({

            "type": "error",

            "message": "Missing token"
        })

        await websocket.close(
            code=1008
        )

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

            raise JWTError(
                "Missing sub claim"
            )

        logger.info(
            f"Authenticated websocket "
            f"user={user_id}"
        )

        await websocket.accept()

        await metrics_service.set_active_websockets(
            ws_manager.connection_count()
        )

        logger.info(
            "WebSocket connection accepted"
        )

    except JWTError as e:

        logger.warning(
            f"JWT verification failed: "
            f"{str(e)}"
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

                timeout=60,
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

                    await websocket.send_json({

                        "type": "error",

                        "message":
                        "Invalid conversation"
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

                event = ChatEvent(

                    request_id=request_id,

                    user_id=int(user_id),

                    conversation_id=int(
                        conversation_id
                    ),

                    query=message,
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

                await ws_manager.connect(

                    request_id,

                    websocket,
                )

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

                if "request_id" in locals():

                    await ws_manager.disconnect(
                        request_id
                    )

                    await metrics_service.set_active_websockets(
                        ws_manager.connection_count()
                    )

                logger.info(

                    f"Streaming disconnected "
                    f"user={user_id}"
                )

                break

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

        if request_id:

            await ws_manager.disconnect(
                request_id
            )

            await metrics_service.set_active_websockets(
                ws_manager.connection_count()
            )

    except Exception as e:

        logger.exception(

            f"WebSocket error "
            f"user={user_id} "
            f"error={str(e)}"
        )

        try:

            logger.info(

                f"Closing websocket "
                f"user={user_id}"
            )

            await websocket.close()

        except Exception as close_error:

            logger.warning(

                f"WebSocket close failed: "
                f"{str(close_error)}"
            )