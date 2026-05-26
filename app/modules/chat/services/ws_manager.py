from fastapi import WebSocket


class WSConnectionManager:

    def __init__(self):

        self.connections = {}

    async def connect(

        self,

        request_id: str,

        websocket: WebSocket,
    ):

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


ws_manager = (
    WSConnectionManager()
)