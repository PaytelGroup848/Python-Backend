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

from app.core.security import (
    verify_token
)

from app.modules.auth.repositories.user_repository import (
    user_repository
)


async def get_current_user(

    db: AsyncSession = Depends(
        get_db
    ),

    token_data=Depends(
        verify_token
    )

):

    user = await (

        user_repository
        .get_by_id(

            db=db,

            user_id=token_data["user_id"]

        )

    )

    if user is None:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="User not found"

        )

    if not user.is_active:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="User account is inactive"

        )

    return user