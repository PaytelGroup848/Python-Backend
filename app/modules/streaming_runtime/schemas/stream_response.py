from pydantic import (
    BaseModel
)


class StreamResponse(
    BaseModel
):

    token: str

    finished: bool = False