from datetime import datetime

from pydantic import BaseModel


class ConnectorInstanceResponse(
    BaseModel
):

    id: int

    connector_implementation_id: int

    organization_id: int | None = None

    name: str

    instance_code: str

    description: str | None = None

    status: str

    configuration_json: dict

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True