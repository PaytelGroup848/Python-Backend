from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.api_keys.services.api_key_auth_service import (
    api_key_auth_service
)

security = HTTPBearer()


async def validate_api_key(

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    api_key = (
        credentials.credentials
    )

    user = await (
        api_key_auth_service
        .validate_key(
            db,
            api_key
        )
    )

    if not user:

        raise HTTPException(

            status_code=401,

            detail="Invalid API Key"
        )

    return user