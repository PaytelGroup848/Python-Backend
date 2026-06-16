from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.core.security import (
    require_role
)

from app.modules.billing.services.plan_service import (
    plan_service
)

from app.modules.billing.services.plan_management_service import (
    plan_management_service
)

from app.modules.billing.schemas.plan_schema import (
    CreatePlanRequest,
    CreatePlanVersionRequest,
    CreatePlanPriceRequest,
    UpdatePlanVersionRequest,
    UpdatePlanPriceRequest
)

router = APIRouter(

    prefix="/admin/plans",

    tags=["Admin Plans"]
)


@router.get("")
async def get_plans(

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    plans = await (
        plan_service
        .get_all_plans(
            db
        )
    )

    return {

        "count":
            len(plans),

        "plans": [

            {
                "id":
                    plan.id,

                "plan_code":
                    plan.plan_code,

                "plan_name":
                    plan.plan_name,

                "description":
                    plan.description,

                "is_public":
                    plan.is_public,

                "is_active":
                    plan.is_active,

                "created_at":
                    plan.created_at,

                "updated_at":
                    plan.updated_at
            }

            for plan in plans
        ]
    }

@router.get(
    "/{plan_id}/versions"
)
async def get_plan_versions(

    plan_id: int,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    versions = await (
        plan_service
        .get_plan_versions(
            db,
            plan_id
        )
    )

    return {

        "count":
            len(versions),

        "versions": [

            {
                "id":
                    version.id,

                "plan_id":
                    version.plan_id,

                "version_number":
                    version.version_number,

                "monthly_token_limit":
                    version.monthly_token_limit,

                "monthly_request_limit":
                    version.monthly_request_limit,

                "monthly_cost_limit":
                    version.monthly_cost_limit,

                "is_active":
                    version.is_active,

                "created_at":
                    version.created_at
            }

            for version in versions
        ]
    }

@router.get(
    "/{plan_id}/prices"
)
async def get_plan_prices(

    plan_id: int,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    prices = await (
        plan_service
        .get_plan_prices(
            db,
            plan_id
        )
    )

    return {

        "count":
            len(prices),

        "prices": [

            {
                "id":
                    price.id,

                "plan_version_id":
                    price.plan_version_id,

                "provider":
                    price.provider,

                "external_price_id":
                    price.external_price_id,

                "currency":
                    price.currency,

                "amount":
                    float(price.amount),

                "billing_cycle":
                    price.billing_cycle,

                "is_active":
                    price.is_active
            }

            for price in prices
        ]
    }


@router.post("")
async def create_plan(

    payload: CreatePlanRequest,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        plan = await (
            plan_management_service
            .create_plan(

                db=db,

                plan_code=
                    payload.plan_code,

                plan_name=
                    payload.plan_name,

                description=
                    payload.description,

                is_public=
                    payload.is_public
            )
        )

        return {

            "message":
                "Plan created successfully",

            "plan": {

                "id":
                    plan.id,

                "plan_code":
                    plan.plan_code,

                "plan_name":
                    plan.plan_name,

                "description":
                    plan.description,

                "is_public":
                    plan.is_public,

                "is_active":
                    plan.is_active
            }
        }

    except ValueError as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )


@router.post(
    "/{plan_id}/versions"
)
async def create_plan_version(

    plan_id: int,

    payload: CreatePlanVersionRequest,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        version = await (

            plan_management_service
            .create_plan_version(

                db=db,

                plan_id=
                    plan_id,

                version_number=
                    payload.version_number,

                monthly_token_limit=
                    payload.monthly_token_limit,

                monthly_request_limit=
                    payload.monthly_request_limit,

                monthly_cost_limit=
                    payload.monthly_cost_limit
            )
        )

        return {

            "message":
                "Plan version created successfully",

            "version": {

                "id":
                    version.id,

                "plan_id":
                    version.plan_id,

                "version_number":
                    version.version_number,

                "monthly_token_limit":
                    version.monthly_token_limit,

                "monthly_request_limit":
                    version.monthly_request_limit,

                "monthly_cost_limit":
                    version.monthly_cost_limit,

                "is_active":
                    version.is_active
            }
        }

    except ValueError as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )

@router.put(
    "/versions/{version_id}"
)
async def update_plan_version(

    version_id: int,

    payload: UpdatePlanVersionRequest,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        version = await (

            plan_management_service
            .update_plan_version(

                db=db,

                version_id=
                    version_id,

                monthly_token_limit=
                    payload.monthly_token_limit,

                monthly_request_limit=
                    payload.monthly_request_limit,

                monthly_cost_limit=
                    payload.monthly_cost_limit
            )
        )

        return {

            "message":
                "Plan version updated successfully",

            "version": {

                "id":
                    version.id,

                "plan_id":
                    version.plan_id,

                "version_number":
                    version.version_number,

                "monthly_token_limit":
                    version.monthly_token_limit,

                "monthly_request_limit":
                    version.monthly_request_limit,

                "monthly_cost_limit":
                    version.monthly_cost_limit,

                "is_active":
                    version.is_active
            }
        }

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)
        )
    
@router.put(
    "/prices/{price_id}"
)
async def update_plan_price(

    price_id: int,

    payload: UpdatePlanPriceRequest,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        price = await (

            plan_management_service
            .update_plan_price(

                db=db,

                price_id=
                    price_id,

                provider=
                    payload.provider,

                currency=
                    payload.currency,

                amount=
                    payload.amount,

                billing_cycle=
                    payload.billing_cycle,

                external_price_id=
                    payload.external_price_id
            )
        )

        return {

            "message":
                "Price updated successfully",

            "price": {

                "id":
                    price.id,

                "provider":
                    price.provider,

                "currency":
                    price.currency,

                "amount":
                    float(
                        price.amount
                    ),

                "billing_cycle":
                    price.billing_cycle,

                "external_price_id":
                    price.external_price_id,

                "is_active":
                    price.is_active
            }
        }

    except ValueError as e:

        raise HTTPException(

            status_code=404,

            detail=str(e)
        )

@router.post(
    "/{plan_id}/prices"
)
async def create_plan_price(

    plan_id: int,

    payload: CreatePlanPriceRequest,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    plan = await (
        plan_service
        .get_by_id(
            db,
            plan_id
        )
    )

    if not plan:

        raise HTTPException(

            status_code=404,

            detail="Plan not found"
        )

    version = await (
        plan_service
        .get_active_version(
            db,
            plan_id
        )
    )

    if not version:

        raise HTTPException(

            status_code=404,

            detail=
                "Active plan version not found"
        )

    try:

        price = await (

            plan_management_service
            .create_plan_price(

                db=db,

                plan_version_id=
                    version.id,

                provider=
                    payload.provider,

                currency=
                    payload.currency,

                amount=
                    payload.amount,

                billing_cycle=
                    payload.billing_cycle,

                external_price_id=
                    payload.external_price_id
            )
        )

        return {

            "message":
                "Plan price created successfully",

            "price": {

                "id":
                    price.id,

                "plan_version_id":
                    price.plan_version_id,

                "provider":
                    price.provider,

                "external_price_id":
                    price.external_price_id,

                "currency":
                    price.currency,

                "amount":
                    float(price.amount),

                "billing_cycle":
                    price.billing_cycle,

                "is_active":
                    price.is_active
            }
        }

    except ValueError as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )