from pydantic import BaseModel


class LoadModelRequest(
    BaseModel
):

    release_id: int