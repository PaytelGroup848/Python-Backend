from pydantic import BaseModel


class CorpusSourceCreate(
    BaseModel
):

    corpus_id: int

    source_type: str

    source_reference: str

    status: str