
from fastapi import WebSocket


class WSConnectionManager:

    def __init__(self):

        self.connections: dict[
            str,
            WebSocket
        ] = {}


    async def connect(

        self,

        request_id: str,

        websocket: WebSocket,
    ):

        await websocket.accept()

        self.connections[
            request_id
        ] = websocket


    def disconnect(

        self,

        request_id: str,
    ):

        self.connections.pop(
            request_id,
            None,
        )


    def get_connection(

        self,

        request_id: str,
    ):

        return self.connections.get(
            request_id
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
