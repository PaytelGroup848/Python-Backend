from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):

    session_id: Optional[str] = None

    conversation_id: Optional[int] = None

    assistant_id: Optional[int] = None

    message: str