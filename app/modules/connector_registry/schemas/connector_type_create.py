from pydantic import BaseModel


class ConnectorTypeCreate(
    BaseModel
):

    code: str

    display_name: str

    description: str | None = None

    is_active: bool