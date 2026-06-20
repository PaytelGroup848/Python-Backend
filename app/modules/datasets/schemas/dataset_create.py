from pydantic import BaseModel


class DatasetCreate(
    BaseModel
):

    name: str

    domain: str

    version: str

    description: str | None = None

    source: str | None = None