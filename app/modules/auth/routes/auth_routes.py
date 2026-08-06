import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas.auth_schema import (

    TokenResponse,

    RegisterRequest,

    LoginRequest,

    RefreshTokenResponse
)



from app.schemas.user_schema import UserResponse
from app.schemas.common_schema import MessageResponse

from app.modules.auth.services.auth_service import AuthService

from app.db.database import AsyncSessionLocal

from app.core.security import (

    create_access_token,

    create_refresh_token,

    SECRET_KEY,

    ALGORITHM
)

from app.models.session import Session as UserSession

from jose import jwt



from fastapi import Request

from app.services.security_service import (
    is_locked,
    record_failed_attempt,
    clear_failed_attempts
)

from app.db.redis_client import redis_client


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_service = AuthService()

# DB dependency
async def get_db():

    async with AsyncSessionLocal() as db:
       yield db

   



#  SIGNUP
@router.post(
    "/signup",
    status_code=201,
    response_model=UserResponse
)
async def signup(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        user = await auth_service.create_user(
            db=db,
            name=req.name,
            email=req.email,
            password=req.password
        )

        return UserResponse.model_validate(user)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    
    except Exception as e:

        await db.rollback()

        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    
# FORGOT PASSWORD
@router.post(
    "/forgot-password",
    status_code=200
)
async def forgot_password(
    email: str
):

    return {
        "message":
        "Password reset link sent"
    }

#  LOGIN
@router.post(
    "/login",
    status_code=200,
    response_model=TokenResponse
)
async def login(
    request: Request,
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    ip = (

        request.client.host

        if request.client

        else "unknown"
    )
    if await is_locked(req.email, ip):
       raise HTTPException(
           status_code=403,
           detail="Too many failed attempts. Try again later."
        )

    # authenticate user
    try:

        user = await asyncio.wait_for(

            auth_service.authenticate_user(
                db,
                req.email,
                req.password
            ),

            timeout=30,
        )

    except asyncio.TimeoutError:

        await record_failed_attempt(
            req.email,
            ip
        )

        raise HTTPException(
            status_code=504,
            detail="Authentication timeout"
        )

    except Exception:

        await record_failed_attempt(
            req.email,
            ip
        )

        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )
    
    if not user:

        await record_failed_attempt(
            req.email,
            ip
        )

        logger.warning(
            f"Login failed for email: {req.email}"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    await clear_failed_attempts(req.email, ip)
    logger.info(
        f"Login success: {user.id}"
    )

    # create access token
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    # create refresh token
    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": user.role
    })

    # save session in database
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token
    )

    try:

        db.add(session)

        await db.commit()

        await db.refresh(session)

    except Exception:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Session creation failed"
        )

    user_display_name = getattr(user, "name", None) or user.email.split("@")[0].capitalize()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user_display_name,
            "role": user.role or "MEMBER",
        }
    }

@router.post(
    "/refresh",
    status_code=200,
    response_model=RefreshTokenResponse
)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):

    result = await asyncio.wait_for(

        db.execute(
            select(UserSession).where(
                UserSession.refresh_token
                == refresh_token
            )
        ),

        timeout=30,
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Expired or invalid refresh token"
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    new_access_token = create_access_token({
        "sub": user_id,
        "role": role
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post(
    "/logout",
    status_code=200,
    response_model=MessageResponse
)
async def logout(
    refresh_token: str,
    
    db: AsyncSession = Depends(get_db)
):

    result = await asyncio.wait_for(

        db.execute(
            select(UserSession).where(
                UserSession.refresh_token
                == refresh_token
            )
        ),

        timeout=30,
    )

    session = result.scalar_one_or_none()

    if session:

        try:

            user_id = session.user_id

            # delete DB session
            await db.delete(session)

            await db.commit()

            # clear Redis memory

            # clear usage tracking
            await redis_client.delete(
                f"usage:{user_id}"
            )

            # clear chat history
            await redis_client.delete(
                f"chat:{user_id}"
            )

            logger.info(
                f"Logout success: {user_id}"
            )

        except Exception:

            await db.rollback()

            raise HTTPException(
                status_code=500,
                detail="Logout failed"
            )

    return {
        "message": "Logged out successfully"
    }