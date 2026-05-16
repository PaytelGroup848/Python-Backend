from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from jose import jwt, JWTError

from app.services.voice_service import (
    speech_to_text
)

from app.services.tts_service import (
    text_to_speech
)

from app.services.agent_service import (
    run_agent
)

from app.db.redis_client import (
    redis_client
)

from app.core.config import settings

router = APIRouter(
    tags=["Voice Assistant"]
)

# -----------------------------
# VERIFY JWT TOKEN
# -----------------------------

def verify_ws_token(
    token: str
):

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ]
        )

        return payload

    except JWTError:

        return None

# -----------------------------
# REALTIME VOICE CHAT
# -----------------------------

@router.websocket("/voice-chat")
async def voice_chat(
    websocket: WebSocket
):

    token = websocket.query_params.get(
        "token"
    )

    if not token:

        await websocket.close(
            code=1008
        )

        return

    user = verify_ws_token(token)

    if not user:

        await websocket.close(
            code=1008
        )

        return

    user_id = user["user_id"]

    await websocket.accept()

    # -----------------------------
    # STORE ACTIVE SESSION
    # -----------------------------

    await redis_client.set(
        f"voice_session:{user_id}",
        "active"
    )

    try:

        while True:

            audio_bytes = await websocket.receive_bytes()

            transcript = await speech_to_text(
                audio_bytes
            )

            # -----------------------------
            # STORE LAST TRANSCRIPT
            # -----------------------------

            await redis_client.set(
                f"voice_last_text:{user_id}",
                transcript
            )

            # -----------------------------
            # RUN AI AGENT
            # -----------------------------

            ai_response = await run_agent(
                user_input=transcript,
                user_id=user_id
            )

            

            # -----------------------------
            # TEXT TO SPEECH
            # -----------------------------

            audio_path = await text_to_speech(
                ai_response
            )

            # -----------------------------
            # SEND RESPONSE
            # -----------------------------

            await websocket.send_json({
                "transcript": transcript,
                "response": ai_response,
                "audio_path": audio_path
            })

    except WebSocketDisconnect:

        print(
            f"Voice disconnected: {user_id}"
        )

    except Exception as e:

        print(
            f"Voice error: {e}"
        )

    finally:

        await redis_client.delete(
            f"voice_session:{user_id}"
        )