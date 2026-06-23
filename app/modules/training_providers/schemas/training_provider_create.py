from pydantic import BaseModel


class TrainingProviderCreate(
    BaseModel
):

    code: str

    display_name: str

    provider_type: str