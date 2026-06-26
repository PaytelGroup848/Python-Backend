from datetime import datetime

from pydantic import BaseModel


class ConnectorImplementationResponse(
    BaseModel
):

    id: int

    connector_type_id: int

    implementation_code: str

    version: str

    status: str

    configuration_schema: str | None = None

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True