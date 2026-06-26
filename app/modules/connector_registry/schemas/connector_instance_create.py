from pydantic import BaseModel


class ConnectorInstanceCreate(
    BaseModel
):

    connector_implementation_id: int

    organization_id: int | None = None

    name: str

    instance_code: str

    description: str | None = None

    status: str

    configuration_json: dict