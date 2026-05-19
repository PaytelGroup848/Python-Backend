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

import os

from app.services.llm_service import (
    get_fastest_response,
    stream_response,
)

router = APIRouter()

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

ALGORITHM = "HS256"


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket
):

    # =========================
    # ACCEPT CONNECTION
    # =========================

    await websocket.accept()

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

            message = data.get(
                "message",
                ""
            )
            conversation_id = data.get(
                "conversation_id"
            )

            async with AsyncSessionLocal() as db:

                user_message = Message(
                  conversation_id=conversation_id,
                  role="user",
                  content=message,
               )

                db.add(user_message)

                await db.commit()

            

            result = await get_fastest_response(
                query=message,
                user_id=int(user_id)
            )

            response_text = (
                result["response"]
            )

            async with AsyncSessionLocal() as db:

                assistant_message = Message(
                   conversation_id=conversation_id,
                   role="assistant",
                   content=response_text,
                )

                db.add(assistant_message)

                await db.commit()

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

    except WebSocketDisconnect:

        print(
            f"Client disconnected user={user_id}"
        )

    except Exception as e:

        print(
            f"WebSocket error: {str(e)}"
        )

        try:

            await websocket.close()

        except:
            pass