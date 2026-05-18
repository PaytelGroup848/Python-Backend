from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

import asyncio

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            data = await websocket.receive_json()

            message = data.get(
                "message",
                ""
            )

            fake_response = (
                f"AI response for: {message}"
            )

            words = fake_response.split()

            for word in words:

                await websocket.send_json({
                    "type": "chunk",
                    "content": word + " ",
                })

                await asyncio.sleep(0.1)

            await websocket.send_json({
                "type": "done"
            })

    except WebSocketDisconnect:

        print(
            "Client disconnected"
        )