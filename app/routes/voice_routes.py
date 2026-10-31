from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.config import settings
from app.db.redis_client import redis_client
from app.services.agent_service import run_agent
from app.services.tts_service import (
    stream_neural_speech,
    text_to_speech,
)
from app.services.voice_service import speech_to_text

router = APIRouter(
    tags=["Voice Assistant"]
)


# -----------------------------
# PYDANTIC SCHEMAS
# -----------------------------

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=15000, description="Text to synthesize")
    voice: Optional[str] = Field(None, description="Optional Microsoft Neural Voice ID")
    rate: Optional[str] = Field("+0%", description="Speech speed adjustment e.g. +10% or -10%")
    pitch: Optional[str] = Field("+0Hz", description="Speech pitch adjustment e.g. +5Hz or -5Hz")


# -----------------------------
# NEURAL STREAMING TTS ENDPOINTS
# -----------------------------

@router.get("/speak", summary="Stream neural speech audio (GET)")
async def stream_speak_get(
    text: str = Query(..., min_length=1, max_length=10000, description="Text to synthesize into speech"),
    voice: Optional[str] = Query(None, description="Optional Edge Neural Voice name"),
    rate: Optional[str] = Query("+0%", description="Speech speed adjustment e.g. +0%"),
    pitch: Optional[str] = Query("+0Hz", description="Speech pitch adjustment e.g. +0Hz"),
):
    """
    Streams Microsoft Azure Neural TTS MP3 audio directly to the browser / HTML5 Audio element.
    Ideal for direct audio streaming without pre-buffering.
    """
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )

    return StreamingResponse(
        stream_neural_speech(text=text, voice=voice, rate=rate, pitch=pitch),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=\"speech.mp3\"",
            "Cache-Control": "public, max-age=3600",
            "Accept-Ranges": "bytes",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/speak", summary="Stream neural speech audio (POST)")
async def stream_speak_post(
    request: SpeakRequest,
):
    """
    Streams Microsoft Azure Neural TTS MP3 audio for longer texts via POST request body.
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty.",
        )

    return StreamingResponse(
        stream_neural_speech(
            text=request.text,
            voice=request.voice,
            rate=request.rate or "+0%",
            pitch=request.pitch or "+0Hz",
        ),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=\"speech.mp3\"",
            "Cache-Control": "no-cache",
            "Accept-Ranges": "bytes",
            "X-Accel-Buffering": "no",
        },
    )


# -----------------------------
# VERIFY JWT TOKEN
# -----------------------------

def verify_ws_token(
    token: str,
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )
        return payload
    except JWTError:
        return None


# -----------------------------
# REALTIME VOICE CHAT
# -----------------------------

@router.websocket("/voice-chat")
async def voice_chat(
    websocket: WebSocket,
):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    user = verify_ws_token(token)

    if not user:
        await websocket.close(code=1008)
        return

    user_id = user["user_id"]

    await websocket.accept()

    # Store active session in Redis
    await redis_client.set(
        f"voice_session:{user_id}",
        "active",
    )

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()

            transcript = await speech_to_text(audio_bytes)

            # Store last transcript
            await redis_client.set(
                f"voice_last_text:{user_id}",
                transcript,
            )

            # Run AI agent
            ai_response = await run_agent(
                user_input=transcript,
                user_id=user_id,
            )

            # Text to speech
            audio_path = await text_to_speech(ai_response)

            # Send response
            await websocket.send_json({
                "transcript": transcript,
                "response": ai_response,
                "audio_path": audio_path,
            })

    except WebSocketDisconnect:
        print(f"Voice disconnected: {user_id}")
    except Exception as e:
        print(f"Voice error: {e}")
    finally:
        await redis_client.delete(f"voice_session:{user_id}")
