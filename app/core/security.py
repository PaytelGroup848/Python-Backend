from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone 
from app.core.config import settings
from sqlalchemy import select


from app.db.database import AsyncSessionLocal
from app.models.user import RolePermission, Permission


#from dotenv import load_dotenv
#-load_dotenv()

#  Load secrets from env
SECRET_KEY = settings.SECRET_KEY

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 1440

REFRESH_TOKEN_EXPIRE_DAYS = 7


#  Auth scheme
security = HTTPBearer()


# =========================
# CREATE TOKEN
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#Refresh Token

def create_refresh_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# VERIFY TOKEN
# =========================
def verify_token(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = int(payload.get("sub"))
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        department = payload.get("department")

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

def require_permission(permission_name: str):

    async def checker(
        user=Depends(verify_token)
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(RolePermission)
                .join(Permission)
                .where(
                    RolePermission.role == user["role"],
                    Permission.name == permission_name
                )
            )

            perms = result.scalar_one_or_none()

            if not perms:

                raise HTTPException(
                    status_code=403,
                    detail="Permission denied"
                )

            return user

    return checker


# =========================
# CURRENT USER
# =========================

#async def get_current_user(

 #   user=Depends(
  #      verify_token
   # )
#):

 #   return type(
  #      "CurrentUser",
   #     (object,),
    #    {
     #       "id": user["user_id"],
      #      "role": user["role"],
       # },
    #)()

