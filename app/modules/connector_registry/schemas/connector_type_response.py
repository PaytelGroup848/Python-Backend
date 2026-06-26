from datetime import datetime

from pydantic import BaseModel


class ConnectorTypeResponse(
    BaseModel
):

    id: int

    code: str

    display_name: str

    description: str | None = None

    is_active: bool

    created_at: datetime

    class Config:

        from_attributes = True