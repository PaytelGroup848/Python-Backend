from pydantic import BaseModel


class IngestionJobCreate(
    BaseModel
):

    corpus_source_id: int

    dataset_id: int | None = None

    status: str

   