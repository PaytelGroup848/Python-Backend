
from fastapi import WebSocket


class WSConnectionManager:

    def __init__(self):

        self.connections: dict[
            str,
            WebSocket
        ] = {}

    async def connect(

        self,

        user_id: str,

        websocket: WebSocket,
    ):

        self.connections[
            str(user_id)
        ] = websocket

    async def disconnect(

        self,

        user_id: str,
    ):

        self.connections.pop(
            str(user_id),
            None,
        )

    def get_connection(

        self,

        user_id: str,
    ):

        return self.connections.get(
            str(user_id)
        )

    def connection_count(
        self
    ) -> int:

        return len(
            self.connections
        )


ws_manager = (
    WSConnectionManager()
)
