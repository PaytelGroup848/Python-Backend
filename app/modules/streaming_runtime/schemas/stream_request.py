from pydantic import (
    BaseModel
)

from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest
)


class StreamRequest(
    BaseModel
):

    inference: InferenceRequest