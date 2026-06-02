from pydantic import BaseModel


class QueueResponse(BaseModel):

    chat_queue: int

    embedding_queue: int

    rag_queue: int

    voice_queue: int