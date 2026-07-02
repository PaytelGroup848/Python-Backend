from pydantic import BaseModel


class LoadModelResponse(
    BaseModel
):

    loaded: bool

    release_id: int

    model_name: str