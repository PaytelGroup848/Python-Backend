from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.admin.services.admin_service import (
    AdminService
)

from app.modules.admin.schemas.admin_schema import (
    DashboardResponse
)
from app.modules.admin.services.provider_service import (
    ProviderService
)

from app.modules.admin.services.worker_service import (
    WorkerService
)

from app.modules.admin.services.queue_service import (
    QueueService
)

from app.modules.admin.services.user_service import (
    UserService
)

from app.modules.billing.services.subscription_service import (
    subscription_service
)

from app.modules.admin.schemas.user_schema import (
    UserListResponse,
    UserStatusUpdate,
    UserPlanUpdate
)



router = APIRouter(
    prefix="/admin",
    tags=["Admin Dashboard"]
)

service = AdminService()

provider_service = ProviderService()

worker_service = WorkerService()

queue_service = QueueService()

user_service = UserService()


@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_dashboard(db)

@router.get("/providers")
async def get_providers():

    return await (
        provider_service
        .get_providers()
    )

@router.get("/workers")
async def get_workers():

    return await (
        worker_service
        .get_workers()
    )

@router.get("/queues")
async def get_queues():

    return await (
        queue_service
        .get_queues()
    )

@router.get(
    "/users",
    response_model=UserListResponse
)
async def get_users(
    db: AsyncSession = Depends(get_db)
):

    return await (
        user_service
        .get_users(db)
    )

@router.patch(
    "/users/{user_id}/status"
)
async def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: AsyncSession = Depends(get_db)
):

    return await (
        user_service.update_user_status(
            db,
            user_id,
            payload.is_active
        )
    )

@router.patch(
    "/users/{user_id}/plan"
)
async def update_user_plan(
    user_id: int,
    payload: UserPlanUpdate,
    db: AsyncSession = Depends(get_db)
):

    try:
        subscription = await (
            subscription_service
            .change_user_plan(
                db,
                user_id,
                payload.plan_name
            )
        )
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err)
        )


    return {

        "message":
            "Plan updated successfully",

        "subscription_id":
            subscription.id,

        "plan_name":
            subscription.plan_name,

        "monthly_token_limit":
            subscription.monthly_token_limit
    }
