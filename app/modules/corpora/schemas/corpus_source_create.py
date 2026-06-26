from pydantic import BaseModel


class CorpusSourceCreate(
    BaseModel
):

    corpus_id: int

    connector_instance_id: int

    source_reference: str

    status: str