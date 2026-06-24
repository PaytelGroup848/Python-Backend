from pydantic import BaseModel


class CorpusCreate(
    BaseModel
):

    name: str

    domain: str

    description: str | None = None

    status: str