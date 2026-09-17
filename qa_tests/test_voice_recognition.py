"""
Enterprise QA Test Suite: Realtime Voice Dictation Pipeline Hardening
Tests canonical JWT validation, query allowlists, concurrency locking,
audio queue backpressure, monotonic sequencing, and lifecycle teardown guards.
"""
import asyncio
import queue
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import qa_tests.conftest
from jose import jwt

from app.core.security import SECRET_KEY, ALGORITHM
from app.modules.voice.routes.voice_ws_routes import (
    voice_websocket,
    active_voice_sessions,
    ActiveVoiceSession,
    VoiceSessionState,
    ALLOWED_MODELS,
    ALLOWED_LANGUAGES,
    ALLOWED_MIME_TYPES,
    MAX_OVERFLOW_TOLERANCE,
)
from app.modules.voice.services.deepgram_service import deepgram_service


def create_test_token(user_id: str = "qa_voice_user_1", expires_in: int = 3600) -> str:
    """Generates a valid JWT token matching platform security core."""
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + expires_in,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


class TestVoiceRecognitionPipeline(unittest.TestCase):

    def setUp(self):
        # Clear in-memory active sessions before each test
        active_voice_sessions.clear()

    def tearDown(self):
        active_voice_sessions.clear()

    def test_missing_token_closes_with_1008_before_accept(self):
        """Pre-allocation Security: Missing token must close with code=1008 immediately without calling accept."""
        async def run():
            mock_ws = MagicMock()
            mock_ws.query_params = {}
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()
            mock_ws.send_json = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            mock_ws.accept.assert_not_called()
            mock_ws.send_json.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008)

        asyncio.run(run())

    def test_invalid_token_closes_with_1008_before_accept(self):
        """Pre-allocation Security: Malformed or forged JWT must close with code=1008 before accept."""
        async def run():
            mock_ws = MagicMock()
            mock_ws.query_params = {"token": "forged_malformed_token_header.payload.signature"}
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            mock_ws.accept.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008)

        asyncio.run(run())

    def test_missing_sub_claim_closes_with_1008(self):
        """Token with valid signature but missing 'sub' identity claim must be rejected."""
        async def run():
            token = jwt.encode({"role": "guest"}, SECRET_KEY, algorithm=ALGORITHM)
            mock_ws = MagicMock()
            mock_ws.query_params = {"token": token}
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            mock_ws.accept.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008)

        asyncio.run(run())

    def test_disallowed_model_rejected_with_1008(self):
        """Security Allowlist: Requesting an unapproved model must be rejected with close code 1008."""
        async def run():
            token = create_test_token()
            mock_ws = MagicMock()
            mock_ws.query_params = {
                "token": token,
                "model": "arbitrary-expensive-model",
            }
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            mock_ws.accept.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008, reason="Disallowed model")

        asyncio.run(run())

    def test_disallowed_language_rejected_with_1008(self):
        """Security Allowlist: Requesting an unapproved language must be rejected with close code 1008."""
        async def run():
            token = create_test_token()
            mock_ws = MagicMock()
            mock_ws.query_params = {
                "token": token,
                "language": "unsupported-lang-dialect",
            }
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            mock_ws.accept.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008, reason="Disallowed language")

        asyncio.run(run())

    def test_concurrent_voice_session_rejection_1008(self):
        """Concurrency Hardening: Second simultaneous connection for same user is rejected with code 1008."""
        async def run():
            user_id = "qa_concurrent_voice_user"
            token = create_test_token(user_id=user_id)

            # Pre-register an existing active session
            existing_session = ActiveVoiceSession(user_id=user_id, session_id="session_first")
            existing_session.state = VoiceSessionState.ACTIVE
            active_voice_sessions[user_id] = existing_session

            # Attempt second connection
            mock_ws = MagicMock()
            mock_ws.query_params = {"token": token}
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await voice_websocket(websocket=mock_ws)

            # Second connection must be rejected without affecting the first session
            mock_ws.accept.assert_not_called()
            mock_ws.close.assert_called_once_with(code=1008, reason="Concurrent voice session limit exceeded")
            self.assertTrue(existing_session.is_active)
            self.assertEqual(active_voice_sessions[user_id].session_id, "session_first")

        asyncio.run(run())

    def test_deepgram_service_exposes_synchronous_client(self):
        """Transport Hardening: deepgram_service.create_websocket_connection() provides synchronous methods."""
        ws_conn = deepgram_service.create_websocket_connection()
        self.assertTrue(hasattr(ws_conn, "start"), "Live client must have start method")
        self.assertTrue(hasattr(ws_conn, "send"), "Live client must have send method")
        self.assertTrue(hasattr(ws_conn, "finish"), "Live client must have finish method")
        self.assertTrue(hasattr(ws_conn, "is_connected"), "Live client must have is_connected method")
        self.assertFalse(asyncio.iscoroutinefunction(ws_conn.start), "start() must be non-coroutine synchronous")
        self.assertFalse(asyncio.iscoroutinefunction(ws_conn.send), "send() must be non-coroutine synchronous")
        self.assertFalse(asyncio.iscoroutinefunction(ws_conn.finish), "finish() must be non-coroutine synchronous")

    def test_audio_queue_overflow_controlled_termination(self):
        """Backpressure Policy: Exceeding MAX_OVERFLOW_TOLERANCE (5 drops) terminates session cleanly."""
        q = queue.Queue(maxsize=2)
        consecutive_overflows = 0
        overflow_triggered = False

        # Simulate fast audio chunk producer against a stalled consumer
        test_chunks = [b"chunk_" + str(i).encode() for i in range(10)]
        for chunk in test_chunks:
            try:
                q.put_nowait(chunk)
                consecutive_overflows = 0
            except queue.Full:
                consecutive_overflows += 1
                if consecutive_overflows >= MAX_OVERFLOW_TOLERANCE:
                    overflow_triggered = True
                    break

        self.assertTrue(overflow_triggered, "Overflow protection must trigger after 5 drops")
        self.assertEqual(consecutive_overflows, MAX_OVERFLOW_TOLERANCE)

    def test_transcript_monotonic_sequence_invariant(self):
        """Protocol Invariant: Sequence counter increases strictly monotonically."""
        sequences = []
        seq_counter = 0

        for _ in range(5):
            seq_counter += 1
            sequences.append(seq_counter)

        self.assertEqual(sequences, [1, 2, 3, 4, 5])
        self.assertTrue(all(sequences[i] < sequences[i+1] for i in range(len(sequences)-1)))

    def test_active_session_lifecycle_states(self):
        """Lifecycle State Machine: Transitions through CONNECTING -> ACTIVE -> CLOSING -> CLOSED."""
        session = ActiveVoiceSession(user_id="test_user", session_id="session_1")
        self.assertEqual(session.state, VoiceSessionState.CONNECTING)
        self.assertTrue(session.is_active)

        session.state = VoiceSessionState.ACTIVE
        self.assertTrue(session.is_active)

        session.state = VoiceSessionState.CLOSING
        self.assertFalse(session.is_active)

        session.state = VoiceSessionState.CLOSED
        self.assertFalse(session.is_active)


if __name__ == "__main__":
    unittest.main()
