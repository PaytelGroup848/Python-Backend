from fastapi import APIRouter, Depends, HTTPException
#from pydantic import BaseModel
#from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.auth_schema import (
    TokenResponse,
    UserRequest,
    RefreshTokenResponse
)

from app.schemas.user_schema import UserResponse
from app.schemas.common_schema import MessageResponse

from app.services.auth_service import AuthService
from app.db.database import AsyncSessionLocal
#from app.services.auth_service import create_user, authenticate_user
from app.core.security import (
    create_access_token,
    create_refresh_token
)
from app.models.session import Session as UserSession
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi import Request

from app.services.security_service import (
    is_locked,
    record_failed_attempt,
    clear_failed_attempts
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_service = AuthService()

# DB dependency
async def get_db():

    db = AsyncSessionLocal()

    try:
        yield db

    finally:
        await db.close()



#  SIGNUP
@router.post(
    "/signup",
    status_code=201,
    response_model=UserResponse
)
async def signup(
    req: UserRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        user = await auth_service.create_user(
            db=db,
            email=req.email,
            password=req.password
        )

        return UserResponse.model_validate(user)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        await db.rollback()

        raise

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

#  LOGIN
@router.post(
    "/login",
    status_code=200,
    response_model=TokenResponse
)
async def login(
    request: Request,
    req: UserRequest,
    db: AsyncSession = Depends(get_db)
):
    ip = request.client.host
    if is_locked(req.email, ip):
       raise HTTPException(
           status_code=403,
           detail="Too many failed attempts. Try again later."
        )

    # authenticate user
    user = await auth_service.authenticate_user(db, req.email, req.password)

    if not user:

       record_failed_attempt(req.email, ip)

       raise HTTPException(
           status_code=401,
           detail="Invalid credentials"
        )
    
    clear_failed_attempts(req.email, ip)

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

        raise

    # return tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
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

    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token == refresh_token
        )
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

    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token == refresh_token
        )
    )

    session = result.scalar_one_or_none()

    if session:

        try:

           await db.delete(session)

           await db.commit()

        except Exception:

            await db.rollback()

            raise

    return {
        "message": "Logged out successfully"
    }