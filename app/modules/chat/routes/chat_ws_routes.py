from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
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

#import os
#import time

import uuid
import asyncio

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

#SECRET_KEY = os.getenv(
 #   "SECRET_KEY"
#)

#ALGORITHM = "HS256"


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket
):

    

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
            f"Authenticated websocket user={user_id}"
        )

        await websocket.accept()

        logger.info(
            "WebSocket connection accepted"
        )

    except JWTError as e:

        logger.warning(
            f"JWT verification failed: {str(e)}"
        )

        await websocket.close(
            code=1008
        )

        return

    # =========================
    # CHAT LOOP
    # =========================

    try:

        while True:

            data = await asyncio.wait_for(

                websocket.receive_json(),

                timeout=60,
            )

            # Skip heartbeat logging

            if data.get("type") == "ping":

               await websocket.send_json({
                   "type": "pong"
               })

               continue

            message = data.get(
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
            conversation_id = data.get(
                "conversation_id"
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
            logger.info(
                f"Rate limit check "
                f"user={user_id}"
            )

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

            async with AsyncSessionLocal() as db:

                conversation = await db.get(
                    ConversationSession,
                    conversation_id
                )

                if (
                    not conversation or
                    conversation.user_id != int(user_id)
                ):

                    await websocket.send_json({
                        "type": "error",
                        "message":
                            "Invalid conversation"
                    })

                    continue

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

    

            #await websocket.send_json({
             #   "type": "start"
            #})

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

                await redis_stream_service.publish(

                    CHAT_REQUEST_STREAM,

                    event.model_dump(),
                )

                await websocket.send_json({

                    "type": "queued",

                    "request_id": request_id,
                })

                await ws_manager.connect(
                    request_id,
                    websocket,
                )

                logger.info(
                    f"Chat request queued "
                    f"user={user_id} "
                    f"request_id={request_id}"
                )
               
               

            except WebSocketDisconnect:

                await ws_manager.disconnect(
                    request_id
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

        break

    except WebSocketDisconnect:

        logger.info(
            f"Client disconnected "
            f"user={user_id}"
        )

    except Exception as e:

        logger.exception(
            f"WebSocket error "
            f"user={user_id}"
        )

        try:

            logger.info(
                f"Closing websocket "
                f"user={user_id}"
            )

            await websocket.close()

        except:
            pass