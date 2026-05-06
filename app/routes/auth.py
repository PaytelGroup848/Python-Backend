from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.auth_service import create_user, authenticate_user
from app.core.security import create_access_token

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
def login(req: UserRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.email, req.password)

    if not user:
        return {"error": "Invalid credentials"}

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {"access_token": token}