from pydantic import BaseModel


class TrainingConfigurationActivate(
    BaseModel,
):

    activate: bool = True