from datetime import datetime
from copy import deepcopy

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training.models.training_configuration import (
    TrainingConfiguration,
)

from app.modules.training.repositories.training_configuration_repository import (
    training_configuration_repository,
)

from app.modules.training.schemas.training_configuration_create import (
    TrainingConfigurationCreate,
)

from app.modules.training.schemas.training_configuration_update import (
    TrainingConfigurationUpdate,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository,
)


class TrainingConfigurationService:

    async def create_configuration(
        self,
        db: AsyncSession,
        data: TrainingConfigurationCreate,
    ) -> TrainingConfiguration:

        existing = await (
            training_configuration_repository
            .get_latest_version(
                db=db,
                configuration_code=(
                    data.configuration_code
                ),
            )
        )

        if existing is not None:

            raise BusinessException(
                "Configuration code already exists. "
                "Use clone to create a new version."
            )
        
        provider = await (
            training_provider_repository
            .get_by_code(
                db=db,
                code=data.runtime_code,
            )
        )

        if provider is None:

            raise BusinessException(
                "Training provider not found."
            )

        if not provider.is_active:

            raise BusinessException(
                "Training provider is inactive."
            )

        configuration = (
            TrainingConfiguration(
                configuration_code=(
                    data.configuration_code
                ),
                display_name=(
                    data.display_name
                ),
                description=(
                    data.description
                ),
                version=1,
                training_type=(
                    data.training_type
                ),
                runtime_code=(
                    data.runtime_code
                ),
                configuration_json=(
                    data.configuration_json
                ),
                created_by=(
                    data.created_by
                ),
                updated_by=(
                    data.created_by
                ),
                is_active=False,
                is_system=False,
            )
        )

        configuration = await (
            training_configuration_repository
            .create(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )

        

        return configuration


    async def get_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
    ) -> TrainingConfiguration:

        configuration = await (
            training_configuration_repository
            .get_by_id(
                db=db,
                training_configuration_id=(
                    configuration_id
                ),
            )
        )

        if configuration is None:

            raise BusinessException(
                "Training configuration not found."
            )

        return configuration


    async def list_configurations(
        self,
        db: AsyncSession,
    ) -> list[TrainingConfiguration]:

        return await (
            training_configuration_repository
            .list_all(
                db=db,
            )
        )


    async def list_active_configurations(
        self,
        db: AsyncSession,
    ) -> list[TrainingConfiguration]:

        return await (
            training_configuration_repository
            .list_active(
                db=db,
            )
        )


    async def update_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
        data: TrainingConfigurationUpdate,
    ) -> TrainingConfiguration:

        configuration = await (
            self.get_configuration(
                db=db,
                configuration_id=(
                    configuration_id
                ),
            )
        )

        if configuration.published_at is not None:

            raise BusinessException(
                "Published configurations are immutable."
            )

        if (
            data.display_name
            is not None
        ):
            configuration.display_name = (
                data.display_name
            )

        if (
            data.description
            is not None
        ):
            configuration.description = (
                data.description
            )

        if (
            data.configuration_json
            is not None
        ):
            configuration.configuration_json = (
                data.configuration_json
            )

        if (
            data.updated_by
            is not None
        ):
            configuration.updated_by = (
                data.updated_by
            )

        configuration.updated_at = (
            datetime.utcnow()
        )

        configuration = await (
            training_configuration_repository
            .update(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )

        

        return configuration
    
    async def clone_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
        created_by: str,
        display_name: str | None = None,
        description: str | None = None,
    ) -> TrainingConfiguration:

        source = await (
            self.get_configuration(
                db=db,
                configuration_id=configuration_id,
            )
        )

        latest = await (
            training_configuration_repository
            .get_latest_version_for_update(
                db=db,
                configuration_code=(
                    source.configuration_code
                ),
            )
        )

        if latest is None:

            raise BusinessException(
                "Unable to determine latest version."
            )

        configuration = (
            TrainingConfiguration(

                configuration_code=(
                    source.configuration_code
                ),

                display_name=(
                    display_name
                    or
                    source.display_name
                ),

                description=(
                    description
                    if description is not None
                    else source.description
                ),

                version=(
                    latest.version + 1
                ),

                training_type=(
                    source.training_type
                ),

                runtime_code=(
                    source.runtime_code
                ),

                configuration_json=(
                    deepcopy(
                        source.configuration_json
                    )
                ),

                created_by=created_by,

                updated_by=created_by,

                published_at=None,

                published_by=None,

                is_active=False,

                is_system=(
                    source.is_system
                ),

            )
        )

        return await (
            training_configuration_repository
            .create(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )
    
    async def activate_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
        updated_by: str,
    ) -> TrainingConfiguration:

        configuration = await (
            training_configuration_repository
            .get_by_id_for_update(
                db=db,
                training_configuration_id=(
                    configuration_id
                ),
            )
        )

        if configuration is None:

            raise BusinessException(
                "Training configuration not found."
            )
        
        await self.validate_runtime_contract(
            configuration
        )

        await (
            training_configuration_repository
            .deactivate_code(
                db=db,
                configuration_code=(
                    configuration.configuration_code
                ),
            )
        )

        configuration.is_active = True

        configuration.updated_by = (
            updated_by
        )

        configuration.updated_at = (
            datetime.utcnow()
        )

        return await (
            training_configuration_repository
            .update(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )
    
    async def deactivate_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
        updated_by: str,
    ) -> TrainingConfiguration:

        configuration = await (
            self.get_configuration(
                db=db,
                configuration_id=configuration_id,
            )
        )

        active_versions = await (
            training_configuration_repository
            .list_versions(
                db=db,
                configuration_code=(
                    configuration.configuration_code
                ),
            )
        )

        active_count = sum(

            1

            for version

            in active_versions

            if version.is_active

        )

        if (

            configuration.is_active

            and

            active_count <= 1

        ):

            raise BusinessException(

                "Cannot deactivate the "
                "last active configuration."

            )

        configuration.is_active = False

        configuration.updated_by = (
            updated_by
        )

        configuration.updated_at = (
            datetime.utcnow()
        )

        return await (
            training_configuration_repository
            .update(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )
    
    async def list_versions(
        self,
        db: AsyncSession,
        configuration_code: str,
    ):

        return await (
            training_configuration_repository
            .list_versions(
                db=db,
                configuration_code=(
                    configuration_code
                ),
            )
        )
    
    async def get_active_configuration(
        self,
        db: AsyncSession,
        configuration_code: str,
    ) -> TrainingConfiguration:

        configuration = await (
            training_configuration_repository
            .get_active_by_code(
                db=db,
                configuration_code=(
                    configuration_code
                ),
            )
        )

        if configuration is None:

            raise BusinessException(
                "Active configuration not found."
            )

        return configuration
    
    async def publish_configuration(
        self,
        db: AsyncSession,
        configuration_id: int,
        published_by: str,
    ) -> TrainingConfiguration:

        configuration = await (
            self.get_configuration(
                db=db,
                configuration_id=(
                    configuration_id
                ),
            )
        )

        await self.validate_runtime_contract(
            configuration
        )

        if (
            configuration.published_at
            is not None
        ):

            raise BusinessException(
                "Configuration is already published."
            )

        configuration.published_by = (
            published_by
        )

        configuration.published_at = (
            datetime.utcnow()
        )

        return await (
            training_configuration_repository
            .update(
                db=db,
                training_configuration=(
                    configuration
                ),
            )
        )
    
    async def validate_runtime_contract(
        self,
        configuration: TrainingConfiguration,
    ) -> None:

        runtime = (
            configuration.configuration_json
        )

        if not isinstance(
            runtime,
            dict,
        ):
            raise BusinessException(
                "Runtime configuration must be an object."
            )

        required_sections = [
 
            "execution",

            "training",

            "tokenizer",

            "formatter",

            "model_initialization",

            "optimizer",

            "scheduler",

            "checkpoint",

            "metrics",

            "final_artifact",

        ]

        for section in required_sections:

            if section not in runtime:

                raise BusinessException(
                    f"Missing runtime section: "
                    f"{section}"
                )

            if not isinstance(
                runtime[section],
                dict,
            ):

                raise BusinessException(
                    f"Runtime section "
                    f"'{section}' "
                    f"must be an object."
                )
            
    async def validate_configuration(
        self,
        configuration: TrainingConfiguration,
    ) -> None:

        if (
            not configuration.configuration_code
        ):

            raise BusinessException(
                "Configuration code missing."
            )

        if (
            not configuration.training_type
        ):

            raise BusinessException(
                "Training type missing."
            )

        if (
            not configuration.runtime_code
        ):

            raise BusinessException(
                "Runtime code missing."
            )

        await self.validate_runtime_contract(
            configuration
        )

    async def can_publish(
        self,
        configuration: TrainingConfiguration,
    ) -> bool:

        try:

            await self.validate_configuration(
                configuration
            )

            return True

        except BusinessException:

            return False


training_configuration_service = (
    TrainingConfigurationService()
)