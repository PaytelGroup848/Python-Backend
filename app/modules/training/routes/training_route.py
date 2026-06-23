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

router = APIRouter(
    prefix="/training",
    tags=["Training"]
)


# =====================================
# Create Training Job
# =====================================

@router.post("/")
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

@router.get(
    "/{training_job_id}"
)
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
    "/{training_job_id}/dispatch"
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