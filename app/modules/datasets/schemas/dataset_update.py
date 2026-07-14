from pydantic import BaseModel


class DatasetUpdate(
    BaseModel
):

    name: str | None = None

    domain: str | None = None

    version: str | None = None

    description: str | None = None

    source: str | None = None

    status: str | None = None