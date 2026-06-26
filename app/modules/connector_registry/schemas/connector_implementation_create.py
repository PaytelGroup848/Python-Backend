from typing import Any

from pydantic import BaseModel


class ConnectorImplementationCreate(BaseModel):

    connector_type_id: int

    implementation_code: str

    version: str

    status: str

    configuration_schema: dict[str, Any] | None = None