from pydantic import BaseModel


class TrainingConfigurationClone(
    BaseModel,
):

    new_version: int