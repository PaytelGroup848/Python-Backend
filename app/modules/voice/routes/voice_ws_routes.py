import asyncio
import logging
import queue
import threading
import time
from enum import Enum
from typing import Dict, Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from jose import jwt, JWTError

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
)
from deepgram import (
    LiveTranscriptionEvents,
    LiveOptions,
)
from app.modules.voice.services.deepgram_service import (
    deepgram_service,
)
from app.db.redis_client import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)

# ==============================================================================
# CONFIGURATION & ALLOWLISTS (STRICT SECURITY BOUNDARY)
# ==============================================================================
ALLOWED_MODELS = {"nova-3", "nova-2"}
ALLOWED_LANGUAGES = {"multi", "en", "hi", "en-in", "en-us"}
ALLOWED_MIME_TYPES = {
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/aac",
    "audio/ogg",
}

DEFAULT_MODEL = "nova-3"
DEFAULT_LANGUAGE = "multi"
MAX_QUEUE_CAPACITY = 50          # ~12.5 seconds buffered at 250ms chunks
MAX_OVERFLOW_TOLERANCE = 5       # Max consecutive queue drops before controlled termination
MAX_SESSION_DURATION = 180.0     # 3 minutes enterprise safety ceiling


class VoiceSessionState(str, Enum):
    CONNECTING = "CONNECTING"
    ACTIVE = "ACTIVE"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"


class ActiveVoiceSession:
    """Tracks per-user active session state to prevent concurrent hijacking."""
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.state = VoiceSessionState.CONNECTING
        self.created_at = time.monotonic()
        self.received_chunks = 0
        self.emitted_sequences = 0

    @property
    def is_active(self) -> bool:
        return self.state in (VoiceSessionState.CONNECTING, VoiceSessionState.ACTIVE)


# Process-local concurrency manager (Thread/coroutine safe)
active_voice_sessions: Dict[str, ActiveVoiceSession] = {}
sessions_lock = asyncio.Lock()


# ==============================================================================
# WEBSOCKET VOICE ENDPOINT (/ws/voice)
# ==============================================================================
@router.websocket("/ws/voice")
async def voice_websocket(
    websocket: WebSocket
):
    # --------------------------------------------------------------------------
    # 1. CANONICAL JWT AUTHENTICATION GATE (Parity with /ws/chat)
    # --------------------------------------------------------------------------
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("Voice WebSocket rejected: Missing token")
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Voice WebSocket rejected: Missing sub claim in token")
            await websocket.close(code=1008)
            return

        logger.info(f"Voice WebSocket authenticated user={user_id}")
    except JWTError as e:
        logger.warning(f"Voice WebSocket JWT verification failed: {type(e).__name__}")
        await websocket.close(code=1008)
        return

    # --------------------------------------------------------------------------
    # 2. QUERY PARAMETERS & ALLOWLIST VALIDATION
    # --------------------------------------------------------------------------
    raw_model = websocket.query_params.get("model", DEFAULT_MODEL)
    model = raw_model.strip().lower() if raw_model else DEFAULT_MODEL
    if model not in ALLOWED_MODELS:
        logger.warning(f"Voice WebSocket rejected disallowed model: {model}")
        await websocket.close(code=1008, reason="Disallowed model")
        return

    raw_lang = websocket.query_params.get("language", DEFAULT_LANGUAGE)
    language = raw_lang.strip().lower() if raw_lang else DEFAULT_LANGUAGE
    if language not in ALLOWED_LANGUAGES:
        logger.warning(f"Voice WebSocket rejected disallowed language: {language}")
        await websocket.close(code=1008, reason="Disallowed language")
        return

    raw_mime = websocket.query_params.get("mimeType", "audio/webm")
    mime_type = raw_mime.strip().lower() if raw_mime else "audio/webm"
    if mime_type not in ALLOWED_MIME_TYPES:
        mime_type = "audio/webm"

    # --------------------------------------------------------------------------
    # 3. ATOMIC SINGLE ACTIVE SESSION CONCURRENCY GATE
    # --------------------------------------------------------------------------
    session_id = f"voice_{user_id}_{int(time.time() * 1000)}"
    session = ActiveVoiceSession(user_id=user_id, session_id=session_id)

    async with sessions_lock:
        existing_session = active_voice_sessions.get(user_id)
        if existing_session and existing_session.is_active:
            logger.warning(
                f"Rejecting second voice session for user={user_id}: "
                f"session={existing_session.session_id} is already active"
            )
            await websocket.close(code=1008, reason="Concurrent voice session limit exceeded")
            return
        active_voice_sessions[user_id] = session

    # Distributed Redis lock with automatic TTL (fail-open if Redis unreachable)
    redis_lock_key = f"voice:session:{user_id}"
    redis_locked = False
    try:
        # Set NX with 180s TTL
        redis_locked = bool(await redis_client.set(redis_lock_key, session_id, ex=int(MAX_SESSION_DURATION), nx=True))
        if not redis_locked:
            # Another process/pod holds an active session lease
            logger.warning(f"Rejecting voice session for user={user_id}: distributed Redis lease already held")
            async with sessions_lock:
                active_voice_sessions.pop(user_id, None)
            await websocket.close(code=1008, reason="Concurrent voice session limit exceeded across cluster")
            return
    except Exception as re:
        # Redis unavailable outside cluster / test environment; fail-open to process-local lock
        logger.debug(f"Redis distributed session lease check bypassed (fail-open): {re}")

    # --------------------------------------------------------------------------
    # 4. ACCEPT WEBSOCKET & INITIALIZE THREAD-BOUND WORKER
    # --------------------------------------------------------------------------
    await websocket.accept()
    loop = asyncio.get_running_loop()

    # Bounded audio queue (async producer -> sync consumer bridge)
    chunk_queue: queue.Queue = queue.Queue(maxsize=MAX_QUEUE_CAPACITY)

    # Deepgram client instance
    dg_connection = deepgram_service.create_websocket_connection()

    # Monotonic transcript sequence counter
    sequence = 0

    def on_transcript(client, *args, **kwargs):
        """Dispatches interim and final transcript events thread-safely."""
        if session.state != VoiceSessionState.ACTIVE:
            return  # Drop late callbacks after session enters CLOSING/CLOSED

        result = kwargs.get("result") or (args[0] if args else None)
        if not result:
            return

        try:
            alternatives = result.channel.alternatives
            if not alternatives:
                return
            transcript = alternatives[0].transcript
        except Exception:
            return

        if not transcript or not transcript.strip():
            return

        is_final = bool(getattr(result, "is_final", False))
        nonlocal sequence
        sequence += 1
        seq = sequence
        session.emitted_sequences = seq

        # Dispatch non-blocking to browser WebSocket
        asyncio.run_coroutine_threadsafe(
            websocket.send_json({
                "type": "transcript",
                "text": transcript.strip(),
                "is_final": is_final,
                "sequence": seq,
            }),
            loop,
        )

    def on_error(client, *args, **kwargs):
        """Handles Deepgram upstream error notification."""
        error = kwargs.get("error") or (args[0] if args else None)
        logger.error(f"Voice session {session_id} Deepgram error: {error}")
        if session.state == VoiceSessionState.ACTIVE:
            asyncio.run_coroutine_threadsafe(
                websocket.send_json({
                    "type": "error",
                    "code": "UPSTREAM_ERROR",
                    "message": str(error),
                }),
                loop,
            )

    dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)

    # --------------------------------------------------------------------------
    # 5. DEDICATED WORKER THREAD & SETUP-PHASE FALLBACK
    # --------------------------------------------------------------------------
    start_event = threading.Event()
    start_success = False
    start_error: Optional[Exception] = None
    chosen_model = model

    def deepgram_worker():
        nonlocal start_success, start_error, chosen_model
        try:
            opts = LiveOptions(
                model=chosen_model,
                language=language,
                smart_format=True,
                interim_results=True,
            )
            res = dg_connection.start(opts)
            if not res and chosen_model == "nova-3":
                logger.warning("nova-3 start returned False; executing setup fallback to nova-2")
                chosen_model = "nova-2"
                opts.model = "nova-2"
                res = dg_connection.start(opts)
            start_success = res
        except Exception as e:
            logger.warning(f"Error starting Deepgram with model={chosen_model}: {e}")
            if chosen_model == "nova-3":
                try:
                    logger.info("Executing setup fallback to nova-2")
                    chosen_model = "nova-2"
                    opts = LiveOptions(
                        model="nova-2",
                        language=language,
                        smart_format=True,
                        interim_results=True,
                    )
                    start_success = dg_connection.start(opts)
                except Exception as e2:
                    start_error = e2
            else:
                start_error = e
        finally:
            start_event.set()

        if not start_success:
            logger.error(f"Deepgram worker setup failed completely: {start_error}")
            return

        # Audio stream consumer loop (owned strictly in worker thread)
        while True:
            try:
                chunk = chunk_queue.get(timeout=1.0)
                if chunk is None:
                    # Sentinel received -> graceful exit
                    break
                dg_connection.send(chunk)
            except queue.Empty:
                if session.state != VoiceSessionState.ACTIVE:
                    break
                continue
            except Exception as se:
                logger.error(f"Error sending audio chunk to Deepgram: {se}")
                break

        # Graceful cleanup strictly inside worker thread
        try:
            dg_connection.finish()
        except Exception as fe:
            logger.debug(f"Deepgram finish cleanup: {fe}")

    worker_thread = threading.Thread(
        target=deepgram_worker,
        name=f"dg_worker_{session_id}",
        daemon=True,
    )
    worker_thread.start()

    # Wait up to 5s for Deepgram handshake
    await asyncio.to_thread(start_event.wait, 5.0)

    if not start_success:
        logger.error(f"Voice session {session_id} aborting: Deepgram handshake failed")
        session.state = VoiceSessionState.CLOSED
        async with sessions_lock:
            active_voice_sessions.pop(user_id, None)
        if redis_locked:
            try:
                await redis_client.delete(redis_lock_key)
            except Exception:
                pass
        await websocket.send_json({
            "type": "error",
            "code": "UPSTREAM_INIT_FAILED",
            "message": "Speech recognition engine failed to connect",
        })
        await websocket.close(code=1011)
        return

    session.state = VoiceSessionState.ACTIVE
    logger.info(f"Voice session {session_id} ACTIVE (model={chosen_model}, lang={language}, mime={mime_type})")

    # --------------------------------------------------------------------------
    # 6. INCOMING AUDIO FRAME LOOP (FASTAPI EVENT LOOP)
    # --------------------------------------------------------------------------
    consecutive_overflows = 0
    start_time = time.monotonic()

    try:
        while True:
            # Enforce maximum session duration ceiling
            if time.monotonic() - start_time > MAX_SESSION_DURATION:
                logger.info(f"Voice session {session_id} reached max duration ({MAX_SESSION_DURATION}s)")
                await websocket.send_json({
                    "type": "info",
                    "code": "MAX_DURATION_REACHED",
                    "message": "Maximum voice recording duration reached",
                })
                break

            audio_chunk = await websocket.receive_bytes()
            if not audio_chunk:
                continue

            session.received_chunks += 1

            # Non-blocking enqueue with explicit overflow policy
            try:
                chunk_queue.put_nowait(audio_chunk)
                consecutive_overflows = 0
            except queue.Full:
                consecutive_overflows += 1
                logger.warning(
                    f"Voice session {session_id} backpressure: queue full "
                    f"({consecutive_overflows}/{MAX_OVERFLOW_TOLERANCE} dropped)"
                )
                if consecutive_overflows >= MAX_OVERFLOW_TOLERANCE:
                    logger.error(f"Voice session {session_id} fatal backpressure overflow. Terminating.")
                    await websocket.send_json({
                        "type": "error",
                        "code": "BUFFER_OVERFLOW",
                        "message": "Voice processing buffer overflow due to network backpressure",
                    })
                    break

    except WebSocketDisconnect:
        logger.info(f"Voice session {session_id} client disconnected")
    except Exception as e:
        logger.error(f"Voice session {session_id} unexpected error: {e}")
    finally:
        # ----------------------------------------------------------------------
        # 7. CLEAN TEARDOWN & LIFECYCLE CLOSURE
        # ----------------------------------------------------------------------
        session.state = VoiceSessionState.CLOSING

        # Send sentinel to unblock worker thread
        try:
            chunk_queue.put_nowait(None)
        except Exception:
            pass

        # Wait up to 3s for worker thread to finish
        if worker_thread.is_alive():
            await asyncio.to_thread(worker_thread.join, 3.0)

        # Transition state to CLOSED (drops any further late callbacks)
        session.state = VoiceSessionState.CLOSED

        # Release local concurrency lock
        async with sessions_lock:
            if active_voice_sessions.get(user_id) is session:
                active_voice_sessions.pop(user_id, None)

        # Release distributed Redis lease
        if redis_locked:
            try:
                await redis_client.delete(redis_lock_key)
            except Exception:
                pass

        logger.info(
            f"Voice session {session_id} CLOSED. "
            f"Total chunks={session.received_chunks}, emitted sequences={session.emitted_sequences}"
        )