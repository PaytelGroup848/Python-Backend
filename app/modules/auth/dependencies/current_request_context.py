from fastapi import (
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

from app.shared.context.request_context import (
    RequestContext
)

from app.modules.auth.dependencies.current_user import (
    get_current_user
)

from app.modules.organizations.services.organization_service import (
    organization_service
)


async def get_request_context(

    db: AsyncSession = Depends(
        get_db
    ),

    current_user=Depends(
        get_current_user
    )

):

    organization = await (

        organization_service
        .get_default_organization_for_user(

            db=db,

            user_id=current_user.id

        )

    )

    if organization is None:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="No active organization."

        )

    return RequestContext(

        user=current_user,

        organization=organization,

        workspace=None

    )