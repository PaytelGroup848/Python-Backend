from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone 
import os

from dotenv import load_dotenv
load_dotenv()

#  Load secrets from env
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#  Auth scheme
security = HTTPBearer()


# =========================
# CREATE TOKEN
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# VERIFY TOKEN
# =========================
def verify_token(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "user_id": user_id,
            "role": role
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# =========================
# ROLE BASED ACCESS
# =========================
def require_role(required_role: str):
    def checker(user=Depends(verify_token)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")

        return user

    return checker

# =========================
# PERMISSION CHECK 
# =========================

from app.db.database import SessionLocal
from app.models.user import RolePermission, Permission
from fastapi import Depends, HTTPException

def require_permission(permission_name: str):
    def checker(user=Depends(verify_token)):
        db = SessionLocal()

        role = user["role"]

        perms = db.query(RolePermission).join(Permission).filter(
            RolePermission.role == role,
            Permission.name == permission_name
        ).first()

        db.close()

        if not perms:
            raise HTTPException(status_code=403, detail="Permission denied")

        return user

    return checker