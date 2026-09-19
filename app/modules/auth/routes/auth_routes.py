import asyncio
import logging
import os
from typing import Optional

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas.auth_schema import (

    TokenResponse,

    RegisterRequest,

    LoginRequest,

    RefreshTokenRequest,

    RefreshTokenResponse,

    LogoutRequest,

    GoogleAuthRequest
)



from app.schemas.user_schema import UserResponse
from app.schemas.common_schema import MessageResponse

from app.modules.auth.services.auth_service import AuthService

from app.db.database import get_db

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
from app.services.guest_service import (
    initialize_guest_user,
    transfer_guest_data
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

auth_service = AuthService()

# =========================
# GUEST SESSION PROVISIONING
# =========================
@router.post(
    "/guest",
    status_code=200,
    response_model=TokenResponse
)
async def guest_session(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    guest_init_id = request.headers.get("x-guest-init-id") or request.cookies.get("guest_init_id")
    try:
        guest_user, access_token, refresh_token = await initialize_guest_user(
            db=db,
            guest_init_id=guest_init_id
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": guest_user.id,
                "email": guest_user.email,
                "full_name": "Guest Visitor",
                "role": "guest",
            }
        }
    except Exception as e:
        logger.exception(f"Guest session provisioning failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize guest session"
        )
@router.post(
    "/signup",
    status_code=201,
    response_model=UserResponse
)
async def signup(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):

    clean_email = req.email.strip().lower()
    clean_name = req.name.strip()

    try:

        user = await auth_service.create_user(
            db=db,
            name=clean_name,
            email=clean_email,
            password=req.password
        )

        user_id = int(user.id)
        user_email = str(user.email)
        user_role = str(user.role or "employee")

        if req.guest_token:
            try:
                await transfer_guest_data(db, req.guest_token, user_id)
            except Exception as mig_err:
                logger.warning(f"Guest migration failed during signup: {mig_err}")

        return UserResponse(
            id=user_id,
            email=user_email,
            role=user_role
        )

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
    clean_email = req.email.strip().lower()

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    elif request.client:
        ip = request.client.host
    else:
        ip = "unknown"

    if await is_locked(clean_email, ip):
       raise HTTPException(
           status_code=403,
           detail="Too many failed attempts. Try again later."
        )

    # authenticate user
    try:

        user = await asyncio.wait_for(

            auth_service.authenticate_user(
                db,
                clean_email,
                req.password
            ),

            timeout=30,
        )

    except asyncio.TimeoutError:
        logger.warning(
            f"Authentication timeout for email: {clean_email} from IP {ip}"
        )
        raise HTTPException(
            status_code=504,
            detail="Authentication service timed out. Please try again."
        )

    except Exception as e:
        logger.exception(
            f"Database or infrastructure error during login for {clean_email} from IP {ip}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Authentication service temporarily unavailable. Please try again."
        )
    
    if not user:
        await record_failed_attempt(
            clean_email,
            ip
        )
        logger.warning(
            f"Login failed: invalid credentials for email: {clean_email}"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    await clear_failed_attempts(clean_email, ip)
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

    user_id = int(user.id)
    user_email = str(user.email)
    user_display_name = getattr(user, "name", None) or user_email.split("@")[0].capitalize()
    user_role = str(getattr(user, "role", "MEMBER") or "MEMBER")

    if req.guest_token:
        try:
            await transfer_guest_data(db, req.guest_token, user_id)
        except Exception as mig_err:
            logger.warning(f"Guest migration failed during login: {mig_err}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_email,
            "full_name": user_display_name,
            "role": user_role,
        }
    }


# =========================
# GOOGLE AUTHENTICATION
# =========================

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "647663692578-u0q685v87qoqjabksdlul3t92g3mlguo.apps.googleusercontent.com"
)

@router.post(
    "/google",
    status_code=200,
    response_model=TokenResponse
)
async def google_auth(
    request: Request,
    req: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    ip = request.client.host if request.client else "unknown"

    # Strict IP-based rate limiting (avoids locking legitimate users on untrusted token inputs)
    rate_limit_key = f"google_auth_ip:{ip}"
    if await is_locked(rate_limit_key, ip):
        raise HTTPException(
            status_code=429,
            detail="Too many attempts from this IP. Try again later."
        )

    # 1. Cryptographic token verification (zero-logging of raw credential or claims)
    try:
        idinfo = id_token.verify_oauth2_token(
            req.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
    except Exception:
        logger.warning(f"Google token verification failed from IP {ip}")
        await record_failed_attempt(rate_limit_key, ip)
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token"
        )

    # 2. Strict OIDC claims validation
    if idinfo.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
        logger.warning(f"Google token rejected: invalid issuer from IP {ip}")
        await record_failed_attempt(rate_limit_key, ip)
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token issuer"
        )

    if idinfo.get("aud") != GOOGLE_CLIENT_ID:
        logger.warning(f"Google token rejected: audience mismatch from IP {ip}")
        await record_failed_attempt(rate_limit_key, ip)
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token audience"
        )

    if not idinfo.get("email_verified", False):
        logger.warning(f"Google token rejected: unverified email from IP {ip}")
        raise HTTPException(
            status_code=401,
            detail="Google account email is not verified"
        )

    raw_email = idinfo.get("email")
    if not raw_email:
        raise HTTPException(
            status_code=401,
            detail="Email claim missing from Google token"
        )

    email = raw_email.strip().lower()
    name = (idinfo.get("name") or email.split("@")[0]).strip()
    google_sub = str(idinfo.get("sub", "")).strip()

    # Clear rate-limit counter on successful verification
    await clear_failed_attempts(rate_limit_key, ip)

    # 3. Authenticate or create user under verified-email policy (password hash untouched)
    try:
        user = await auth_service.authenticate_or_create_google_user(
            db=db,
            email=email,
            name=name,
            google_sub=google_sub
        )
    except ValueError as e:
        raise HTTPException(
            status_code=403 if "inactive" in str(e).lower() else 400,
            detail=str(e)
        )
    except Exception:
        logger.exception("Google user resolution failed")
        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )

    logger.info(f"Google auth success: user_id={user.id}")

    # 4. Issue application access token & refresh token
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "role": user.role
    })

    # 5. Persist user session
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

    user_id = int(user.id)
    user_email = str(user.email)
    user_display_name = getattr(user, "name", None) or user_email.split("@")[0].capitalize()
    user_role = str(getattr(user, "role", "MEMBER") or "MEMBER")

    if req.guest_token:
        try:
            await transfer_guest_data(db, req.guest_token, user_id)
        except Exception as mig_err:
            logger.warning(f"Guest migration failed during google_auth: {mig_err}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "email": user_email,
            "full_name": user_display_name,
            "role": user_role,
        }
    }

@router.post(
    "/refresh",
    status_code=200,
    response_model=RefreshTokenResponse
)
async def refresh_access_token(
    req: Optional[RefreshTokenRequest] = None,
    refresh_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    token = None
    if req and req.refresh_token:
        token = req.refresh_token.strip()
    elif refresh_token:
        token = refresh_token.strip()

    if not token:
        raise HTTPException(
            status_code=422,
            detail="refresh_token is required in request body or query parameter"
        )

    result = await asyncio.wait_for(
        db.execute(
            select(UserSession).where(
                UserSession.refresh_token == token
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
            token,
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
        "sub": str(user_id),
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
    req: Optional[LogoutRequest] = None,
    refresh_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    token = None
    if req and req.refresh_token:
        token = req.refresh_token.strip()
    elif refresh_token:
        token = refresh_token.strip()

    if token:
        try:
            result = await asyncio.wait_for(
                db.execute(
                    select(UserSession).where(
                        UserSession.refresh_token == token
                    )
                ),
                timeout=30,
            )

            session = result.scalar_one_or_none()

            if session:
                user_id = session.user_id
                # Revoke this specific device session
                await db.delete(session)
                await db.commit()
                logger.info(f"Logout session revoked for user_id={user_id}")

        except Exception as e:
            await db.rollback()
            logger.warning(f"Error revoking session during logout: {e}")

    return {
        "message": "Logged out successfully"
    }