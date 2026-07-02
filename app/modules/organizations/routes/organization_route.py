from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.organizations.schemas.organization_create import (
    OrganizationCreate
)

from app.modules.organizations.schemas.organization_update import (
    OrganizationUpdate
)

from app.modules.organizations.schemas.organization_response import (
    OrganizationResponse
)

from app.modules.organizations.services.organization_service import (
    organization_service
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_organization(

    data: OrganizationCreate,

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        organization_service
        .create_organization(
            db=db,
            data=data
        )
    )


@router.get(
    "/",
    response_model=list[OrganizationResponse]
)
async def list_organizations(

    db: AsyncSession = Depends(
        get_db
    )

):

    return await (
        organization_service
        .list_organizations(
            db=db
        )
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def get_organization(

    organization_id: int,

    db: AsyncSession = Depends(
        get_db
    )

):

    organization = await (
        organization_service
        .get_organization(
            db=db,
            organization_id=organization_id
        )
    )

    if not organization:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return organization


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse
)
async def update_organization(

    organization_id: int,

    data: OrganizationUpdate,

    db: AsyncSession = Depends(
        get_db
    )

):

    organization = await (
        organization_service
        .get_organization(
            db=db,
            organization_id=organization_id
        )
    )

    if not organization:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return await (
        organization_service
        .update_organization(
            db=db,
            organization=organization,
            data=data
        )
    )