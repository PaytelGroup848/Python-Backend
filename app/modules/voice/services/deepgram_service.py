from deepgram import (
    DeepgramClient,
)

from app.core.config import settings


class DeepgramService:

    def __init__(self):

        self.client = DeepgramClient(
            settings.DEEPGRAM_API_KEY
        )

    async def create_connection(self):

        return self.client.listen.live.v("1")


deepgram_service = (
    DeepgramService()
)