from deepgram import DeepgramClient

from app.core.config import settings


class DeepgramService:

    def __init__(self):
        self._client = None

    @property
    def client(self) -> DeepgramClient:
        if self._client is None:
            self._client = DeepgramClient(
                settings.DEEPGRAM_API_KEY
            )
        return self._client

    def create_websocket_connection(self):
        """
        Creates a synchronous WebSocket client for live transcription (v1).
        This runs in a dedicated worker thread, completely immune to the websockets 14.x
        extra_headers issue in asynclive and non-blocking for FastAPI event loop.
        """
        return self.client.listen.websocket.v("1")

    def create_connection(self):
        """Backward compatibility shim."""
        return self.create_websocket_connection()


deepgram_service = DeepgramService()

