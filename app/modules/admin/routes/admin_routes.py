import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.generated_image import GeneratedImage
from app.models.user import User

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


@router.get("/media")
async def get_admin_media(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    provider: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * limit

    query = (
        select(
            GeneratedImage.id,
            GeneratedImage.user_id,
            GeneratedImage.conversation_id,
            GeneratedImage.provider,
            GeneratedImage.model_name,
            GeneratedImage.original_prompt,
            GeneratedImage.enhanced_prompt,
            GeneratedImage.file_path,
            GeneratedImage.file_url,
            GeneratedImage.mime_type,
            GeneratedImage.aspect_ratio,
            GeneratedImage.status,
            GeneratedImage.created_at,
            User.name.label("user_name"),
            User.email.label("user_email"),
        )
        .outerjoin(User, GeneratedImage.user_id == User.id)
    )

    count_query = select(func.count(GeneratedImage.id))

    if user_id:
        query = query.filter(GeneratedImage.user_id == user_id)
        count_query = count_query.filter(GeneratedImage.user_id == user_id)

    if provider:
        query = query.filter(GeneratedImage.provider == provider)
        count_query = count_query.filter(GeneratedImage.provider == provider)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(GeneratedImage.original_prompt.ilike(term))
        count_query = count_query.filter(GeneratedImage.original_prompt.ilike(term))

    query = query.order_by(GeneratedImage.id.desc()).offset(offset).limit(limit)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    results = await db.execute(query)
    rows = results.all()

    images = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "conversation_id": r.conversation_id,
            "provider": r.provider,
            "model_name": r.model_name,
            "original_prompt": r.original_prompt,
            "enhanced_prompt": r.enhanced_prompt,
            "file_url": r.file_url,
            "aspect_ratio": r.aspect_ratio,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "user_name": r.user_name or "Anonymous",
            "user_email": r.user_email or "",
        }
        for r in rows
    ]

    return {
        "images": images,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 1,
    }


@router.delete("/media/{image_id}")
async def delete_admin_media(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(GeneratedImage).filter(GeneratedImage.id == image_id)
    )
    img_record = res.scalar_one_or_none()
    if not img_record:
        raise HTTPException(status_code=404, detail="Media asset not found")

    # Remove file from disk if present
    if img_record.file_path:
        full_disk_path = os.path.join(os.getcwd(), img_record.file_path)
        if os.path.exists(full_disk_path):
            try:
                os.remove(full_disk_path)
            except OSError:
                pass

    await db.delete(img_record)
    await db.commit()

    return {"success": True, "message": f"Media asset {image_id} deleted successfully"}
