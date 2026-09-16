"""
BUG-05: Regression Test for WebSocket Protocol Conformance & ASGI Pre-Accept Safety
"""
import asyncio
import inspect
import unittest
from unittest.mock import AsyncMock, MagicMock

import qa_tests.conftest
from app.modules.chat.routes.chat_ws_routes import websocket_chat


class TestBug05WebSocketAuth(unittest.TestCase):

    def test_missing_token_closes_with_1008_without_send_json(self):
        """Negative test: Missing token must close with code=1008 immediately without calling send_json before accept."""
        async def run_test():
            mock_ws = MagicMock()
            mock_ws.query_params = {}
            mock_ws.send_json = AsyncMock()
            mock_ws.accept = AsyncMock()
            mock_ws.close = AsyncMock()

            await websocket_chat(websocket=mock_ws)

            # Must NOT call accept
            mock_ws.accept.assert_not_called()
            # Must NOT call send_json before accept (prevent Starlette ASGI protocol violation)
            mock_ws.send_json.assert_not_called()
            # Must close with 1008 (Policy Violation)
            mock_ws.close.assert_called_once_with(code=1008)

        asyncio.run(run_test())

    def test_idle_timeout_is_180s(self):
        """Verify WebSocket idle receive timeout is set to 180s to tolerate background tab throttling."""
        import inspect
        from app.modules.chat.routes import chat_ws_routes
        source = inspect.getsource(chat_ws_routes.websocket_chat)

        self.assertIn("timeout=180", source, "WebSocket receive timeout must be 180 seconds")


if __name__ == "__main__":
    unittest.main()

