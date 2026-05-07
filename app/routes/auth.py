from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.auth_service import create_user, authenticate_user
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

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserRequest(BaseModel):
    email: str
    password: str

#  SIGNUP
@router.post("/signup")
def signup(req: UserRequest, db: Session = Depends(get_db)):
    user = create_user(db, req.email, req.password)
    return {"message": "User created", "user_id": user.id}

#  LOGIN
@router.post("/login")
def login(request: Request,req: UserRequest,db: Session = Depends(get_db)):
    ip = request.client.host
    if is_locked(req.email, ip):
       raise HTTPException(
           status_code=403,
           detail="Too many failed attempts. Try again later."
        )

    # authenticate user
    user = authenticate_user(db, req.email, req.password)

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

    db.add(session)
    db.commit()

    # return tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token
    ).first()

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

@router.post("/logout")
def logout(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token
    ).first()

    if session:
        db.delete(session)
        db.commit()

    return {
        "message": "Logged out successfully"
    }