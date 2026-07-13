from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.training.schemas.training_job_create import (
    TrainingJobCreate
)

from app.modules.training.services.training_service import (
    training_service
)

from app.modules.training.services.training_dispatch_service import (
    training_dispatch_service
)

from app.modules.training.services.training_configuration_service import (
    training_configuration_service,
)

from app.modules.training.schemas.training_configuration_create import (
    TrainingConfigurationCreate,
)

from app.modules.training.schemas.training_configuration_update import (
    TrainingConfigurationUpdate,
)

router = APIRouter(
    prefix="/training",
    tags=["Training"]
)


# =====================================
# Create Training Job
# =====================================

@router.post("/jobs")
async def create_training_job(

    data: TrainingJobCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    training_job = await (
        training_service
        .create_training_job(
            db,
            data
        )
    )

    

    await db.refresh(
        training_job
    )

    return training_job


# =====================================
# Get Training Job
# =====================================

@router.get("/jobs/{training_job_id}")
async def get_training_job(

    training_job_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        training_service
        .get_training_job(
            db,
            training_job_id
        )
    )


# =====================================
# Dispatch Training Job
# =====================================

@router.post(
    "/jobs/{training_job_id}/dispatch"
)
async def dispatch_training_job(

    training_job_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        training_dispatch_service
        .dispatch(
            db=db,
            training_job_id=training_job_id
        )
    )

# =====================================
# Create Training Configuration
# =====================================

@router.post(
    "/configurations"
)
async def create_training_configuration(

    data: TrainingConfigurationCreate,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .create_configuration(
            db=db,
            data=data,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# List Training Configurations
# =====================================

@router.get(
    "/configurations"
)
async def list_training_configurations(

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        training_configuration_service
        .list_configurations(
            db=db,
        )
    )

# =====================================
# Get Training Configuration
# =====================================

@router.get(
    "/configurations/{configuration_id}"
)
async def get_training_configuration(

    configuration_id: int,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        training_configuration_service
        .get_configuration(
            db=db,
            configuration_id=configuration_id,
        )
    )

# =====================================
# Update Training Configuration
# =====================================

@router.put(
    "/configurations/{configuration_id}"
)
async def update_training_configuration(

    configuration_id: int,

    data: TrainingConfigurationUpdate,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .update_configuration(
            db=db,
            configuration_id=configuration_id,
            data=data,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# Update Training Configuration
# =====================================

@router.put(
    "/configurations/{configuration_id}"
)
async def update_training_configuration(

    configuration_id: int,

    data: TrainingConfigurationUpdate,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .update_configuration(
            db=db,
            configuration_id=configuration_id,
            data=data,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# Clone Training Configuration
# =====================================

@router.post(
    "/configurations/{configuration_id}/clone"
)
async def clone_training_configuration(

    configuration_id: int,

    created_by: str,

    display_name: str | None = None,

    description: str | None = None,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .clone_configuration(
            db=db,
            configuration_id=configuration_id,
            created_by=created_by,
            display_name=display_name,
            description=description,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# Activate Training Configuration
# =====================================

@router.post(
    "/configurations/{configuration_id}/activate"
)
async def activate_training_configuration(

    configuration_id: int,

    updated_by: str,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .activate_configuration(
            db=db,
            configuration_id=configuration_id,
            updated_by=updated_by,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# Publish Training Configuration
# =====================================

@router.post(
    "/configurations/{configuration_id}/publish"
)
async def publish_training_configuration(

    configuration_id: int,

    published_by: str,

    db: AsyncSession = Depends(
        get_db
    ),

):

    configuration = await (
        training_configuration_service
        .publish_configuration(
            db=db,
            configuration_id=configuration_id,
            published_by=published_by,
        )
    )

    await db.commit()

    await db.refresh(
        configuration
    )

    return configuration

# =====================================
# Configuration Version History
# =====================================

@router.get(
    "/configurations/{configuration_code}/versions"
)
async def list_configuration_versions(

    configuration_code: str,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        training_configuration_service
        .list_versions(
            db=db,
            configuration_code=configuration_code,
        )
    )

# =====================================
# Active Configuration
# =====================================

@router.get(
    "/configurations/{configuration_code}/active"
)
async def get_active_configuration(

    configuration_code: str,

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await (
        training_configuration_service
        .get_active_configuration(
            db=db,
            configuration_code=configuration_code,
        )
    )