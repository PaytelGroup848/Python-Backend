from pydantic import (
    BaseModel,
)


class TrainingConfigurationValidation(
    BaseModel,
):

    valid: bool

    message: str