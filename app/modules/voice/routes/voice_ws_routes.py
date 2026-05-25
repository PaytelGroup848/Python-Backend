import asyncio
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

import logging


from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)

from app.modules.voice.services.deepgram_service import (
    deepgram_service
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.websocket("/ws/voice")
async def voice_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    loop = asyncio.get_running_loop()

    dg_connection = (
        await deepgram_service
        .create_connection()
    )

    client = websocket.client

    logger.info(
        f"Voice client connected: "
        f"{client.host}:{client.port}"
    )

    def on_transcript(
        client,
        result,
        **kwargs
    ):
        
        logger.info(f"Deepgram raw result: {result}")

        transcript = (
            result.channel
            .alternatives[0]
            .transcript
        )

        if not result.is_final:
            return

        if transcript:

            logger.info(
                f"Transcript: {transcript}"
            )

            

            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "transcript",
                    "text": transcript
                }),  
                loop
            )


    dg_connection.on(
        LiveTranscriptionEvents.Transcript,
        on_transcript
    )

    options = LiveOptions(
        model="nova-2",
        language="en-US",
        smart_format=True,
        interim_results=True,
    )

    dg_connection.start(
        options
    )


    try:

        while True:

            audio_chunk = (
                await websocket.receive_bytes()
            )

            dg_connection.send(
                audio_chunk
            )


            logger.info(
                f"Received audio chunk: "
                f"{len(audio_chunk)} bytes"
            )

            

    except WebSocketDisconnect:

        logger.info(
            "Voice websocket disconnected"
        )

    except Exception as e:

        logger.error(
            f"Voice websocket error: {e}"
        )

    finally:

       try:

           dg_connection.finish()

       except Exception:

           pass

       logger.info(
           "Voice websocket cleanup complete"
       )