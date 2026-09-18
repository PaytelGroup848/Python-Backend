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
from app.shared.redis.client import redis_client
from app.services.guest_service import (
    reserve_guest_credit,
    refund_guest_credit,
    get_guest_credits
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
        role = payload.get("role", "employee")

        if not user_id:
            raise JWTError("Missing sub claim")

        logger.info(
            f"Authenticated websocket user={user_id} role={role}"
        )

        await websocket.accept()
        await websocket_manager.connect(user_id, websocket)

        logger.info(
            "WebSocket connection accepted"
        )

        # Reactive credit broadcast for guest users
        if role == "guest":
            credits_left = await get_guest_credits(user_id)
            rem = credits_left if credits_left is not None else 0
            await websocket.send_json({
                "type": "credits_update",
                "credits_remaining": rem,
                "remaining": rem,
            })

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
                # ATOMIC GUEST QUOTA RESERVATION
                # =========================
                request_id = str(uuid.uuid4())

                if role == "guest":
                    res_status, remaining_credits = await reserve_guest_credit(user_id)
                    if res_status == 0:
                        # 0 free credits remaining
                        await websocket.send_json({
                            "type": "error",
                            "code": "CREDITS_LIMIT_REACHED",
                            "message": "Your free guest credit limit has been reached. Please sign in or create an account to continue.",
                            "credits_remaining": 0
                        })
                        continue
                    elif res_status == -1:
                        # Session / quota expired or missing
                        await websocket.send_json({
                            "type": "error",
                            "code": "GUEST_SESSION_EXPIRED",
                            "message": "Your guest session has expired. Please sign in or create an account to continue.",
                            "credits_remaining": 0
                        })
                        continue
                    else:
                        # Credit reserved: broadcast reactive update immediately
                        await websocket.send_json({
                            "type": "credits_update",
                            "credits_remaining": remaining_credits,
                            "remaining": remaining_credits,
                        })
                        try:
                            await redis_client.set(f"guest:prompt_state:{request_id}", "RESERVED", ex=3600)
                            await redis_client.set(f"guest:request_user:{request_id}", str(user_id), ex=3600)
                        except Exception as tag_err:
                            logger.warning(f"Failed setting guest prompt state tag: {tag_err}")

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

                except Exception as db_err:

                    await db.rollback()
                    logger.exception(f"Failed to persist user message for user={user_id}: {db_err}")

                    if role == "guest":
                        try:
                            await refund_guest_credit(user_id, request_id)
                            cur_val = await get_guest_credits(user_id)
                            rem = cur_val if cur_val is not None else 0
                            await websocket.send_json({
                                "type": "credits_update",
                                "credits_remaining": rem,
                                "remaining": rem,
                            })
                        except Exception:
                            pass

                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to save message. Please try again."
                    })
                    continue

            # =========================
            # QUEUE REQUEST
            # =========================

            try:

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

                    if role == "guest":
                        try:
                            await refund_guest_credit(user_id, request_id)
                            cur_val = await get_guest_credits(user_id)
                            rem = cur_val if cur_val is not None else 0
                            await websocket.send_json({
                                "type": "credits_update",
                                "credits_remaining": rem,
                                "remaining": rem,
                            })
                        except Exception:
                            pass

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
            except Exception as pub_exc:
                logger.exception(f"Error publishing chat request for user={user_id} req={request_id}: {pub_exc}")
                if role == "guest":
                    try:
                        await refund_guest_credit(user_id, request_id)
                        cur_val = await get_guest_credits(user_id)
                        rem = cur_val if cur_val is not None else 0
                        await websocket.send_json({
                            "type": "credits_update",
                            "credits_remaining": rem,
                            "remaining": rem,
                        })
                    except Exception:
                        pass
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to queue message. Please try again."
                })
                continue
            

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

