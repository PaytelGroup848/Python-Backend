from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.repositories.connector_instance_repository import (
    connector_instance_repository
)

from app.modules.connector_registry.repositories.connector_implementation_repository import (
    connector_implementation_repository
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class ConnectorExecutionService:

    async def execute(
        self,
        db: AsyncSession,
        connector_instance_id: int,
        configuration: dict | None = None
    ) -> dict:

        connector_instance = await (
            connector_instance_repository
            .get_by_id(
                db,
                connector_instance_id
            )
        )

        if not connector_instance:

            raise BusinessException(
                "Connector instance not found."
            )

        connector_implementation = await (
            connector_implementation_repository
            .get_by_id(
                db,
                connector_instance.connector_implementation_id
            )
        )

        if not connector_implementation:

            raise BusinessException(
                "Connector implementation not found."
            )

        #
        # Runtime execution will be plugged in here.
        #
        # Google Drive
        # Dropbox
        # S3
        # SharePoint
        # GitHub
        #
        # No implementation-specific logic belongs here.
        #

        metrics = {

            "connector_instance_id": connector_instance.id,

            "connector_implementation_id": connector_implementation.id,

            "status": "SUCCESS"
        }

        return metrics


connector_execution_service = (
    ConnectorExecutionService()
)