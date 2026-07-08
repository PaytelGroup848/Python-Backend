from pydantic import BaseModel


class DataPipelineCreate(
    BaseModel
):

    corpus_id: int

    name: str

    pipeline_code: str

    dataset_id: int | None = None

    status: str