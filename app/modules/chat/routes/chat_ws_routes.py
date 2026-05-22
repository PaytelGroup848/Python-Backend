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
import time

from app.core.logger import (
    logger,
)

from app.services.llm_service import (
    get_fastest_response,
    stream_response,
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
    # ACCEPT CONNECTION
    # =========================

    await websocket.accept()

    logger.info(
        "WebSocket connection accepted"
    )

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

        user_id = payload.get(
            "sub"
        )

        logger.info(
            f"Authenticated websocket user={user_id}"
        )

        if not user_id:

            await websocket.send_json({
                "type": "error",
                "message": "Invalid token"
            })

            await websocket.close(
                code=1008
            )

            return
        


    except JWTError:

        logger.warning(
            "JWT verification failed"
        )

        await websocket.send_json({
            "type": "error",
            "message": "JWT verification failed"
        })

        await websocket.close(
            code=1008
        )

        return

    # =========================
    # CHAT LOOP
    # =========================

    try:

        while True:

            data = await websocket.receive_json()

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

                try:

                    user_message = Message(
                       conversation_id=conversation_id,
                       role="user",
                       content=message,
                    )

                    db.add(user_message)

                    await db.commit()

                except Exception:

                    await db.rollback()

                    raise

            try:

                logger.info(
                    f"Generating AI response "
                    f"user={user_id}"
                )

                start_time = time.perf_counter()

                result = await get_fastest_response(
                    query=message,
                    user_id=int(user_id)
                )

                response_text = (
                    result["response"]
                )

                latency = (
                    time.perf_counter()
                    - start_time
                )

                logger.info(
                    f"AI response generated "
                    f"user={user_id} "
                    f"latency={latency:.2f}s"
                )

            except Exception:

                logger.exception(
                    f"AI generation failed "
                    f"user={user_id}"
                )

                try:

                    await websocket.send_json({
                        "type": "error",
                        "message":
                            "AI generation failed"
                    })

                except WebSocketDisconnect:

                    logger.info(
                        f"Client disconnected "
                        f"during AI failure "
                        f"user={user_id}"
                    )

                    break

                continue


            

            

            #await websocket.send_json({
             #   "type": "start"
            #})

            try:

               await websocket.send_json({
                   "type": "start"
               })

               async for chunk in stream_response(
                  response_text
               ):

                  await websocket.send_json({
                      "type": "chunk",
                      "content": chunk,
                  })

               await websocket.send_json({
                   "type": "done"
              })
               
               async with AsyncSessionLocal() as db:

                  try:

                     assistant_message = Message(
                         conversation_id=conversation_id,
                         role="assistant",
                         content=response_text,
                     )

                     db.add(assistant_message)

                     await db.commit()

                  except Exception:

                      await db.rollback()

                      raise

            except WebSocketDisconnect:

                logger.info(
                    f"Streaming disconnected "
                    f"user={user_id}"
                )

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