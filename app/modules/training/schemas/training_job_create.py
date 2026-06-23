from pydantic import BaseModel


class TrainingJobCreate(
    BaseModel
):

    dataset_id: int

    training_provider_id: int

    base_model: str

    training_type: str