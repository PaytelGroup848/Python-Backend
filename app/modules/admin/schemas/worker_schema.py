from pydantic import BaseModel


class WorkerStatus(BaseModel):

    name: str

    status: str

    queue_size: int


class WorkerListResponse(BaseModel):

    workers: list[WorkerStatus]