from pydantic import BaseModel


class ModelGenerationResponse(
    BaseModel
):

    text: str

    model_version_id: int

    deployment_name: str