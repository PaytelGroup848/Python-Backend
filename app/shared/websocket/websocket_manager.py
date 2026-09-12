
import logging
from typing import Dict, Optional, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSConnectionManager:

    def __init__(self):
        # request_id -> WebSocket
        self.request_connections: Dict[str, WebSocket] = {}
        # user_id -> Set of WebSockets
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> Set of request_ids for fast cleanup
        self.socket_requests: Dict[WebSocket, Set[str]] = {}

    async def connect(
        self,
        user_id: str,
        websocket: WebSocket,
    ):
        uid = str(user_id)
        if uid not in self.user_connections:
            self.user_connections[uid] = set()
        self.user_connections[uid].add(websocket)
        self.socket_requests[websocket] = set()

    async def disconnect(
        self,
        user_id: str,
        websocket: Optional[WebSocket] = None,
    ):
        uid = str(user_id)
        if websocket:
            req_ids = self.socket_requests.pop(websocket, set())
            for req_id in req_ids:
                self.request_connections.pop(req_id, None)
            if uid in self.user_connections:
                self.user_connections[uid].discard(websocket)
                if not self.user_connections[uid]:
                    self.user_connections.pop(uid, None)
        else:
            self.user_connections.pop(uid, None)

    def register_request(self, request_id: str, websocket: WebSocket):
        rid = str(request_id)
        self.request_connections[rid] = websocket
        if websocket in self.socket_requests:
            self.socket_requests[websocket].add(rid)

    def unregister_request(self, request_id: str):
        rid = str(request_id)
        ws = self.request_connections.pop(rid, None)
        if ws and ws in self.socket_requests:
            self.socket_requests[ws].discard(rid)

    def get_connection(
        self,
        identifier: str,
    ) -> Optional[WebSocket]:
        req_conn = self.request_connections.get(str(identifier))
        if req_conn:
            return req_conn
        user_conns = self.user_connections.get(str(identifier))
        if user_conns:
            return next(iter(user_conns))
        return None

    @property
    def connections(self):
        return self.request_connections

    def connection_count(
        self
    ) -> int:
        return len(
            self.request_connections
        )


websocket_manager = (
    WSConnectionManager()
)
