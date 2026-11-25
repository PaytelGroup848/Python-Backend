import logging
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.auth.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class AuthService:

    def __init__(self):

        self.user_repository = UserRepository()

    def hash_password(
        self,
        password: str
    ) -> str:

        password_bytes = password.encode("utf-8")

        if len(password_bytes) > 72:
            raise ValueError(
                "Password exceeds bcrypt limit"
            )

        return pwd_context.hash(password)

    def verify_password(
        self,
        password: str,
        hashed_password: str
    ) -> bool:
        if not password or not hashed_password:
            return False
        try:
            return pwd_context.verify(
                password,
                hashed_password
            )
        except Exception:
            logger.warning("Password verification failed due to invalid or malformed hash format.")
            return False

    async def create_user(
        self,
        db: AsyncSession,
        name: str,
        email: str,
        password: str,
        city: Optional[str] = None,
        country: Optional[str] = None
    ) -> User:

        clean_email = email.strip().lower() if email else ""
        clean_name = name.strip() if name else ""

        existing_user = await self.user_repository.get_by_email(
            db=db,
            email=clean_email
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        hashed_password = self.hash_password(password)

        user = User(
            name=clean_name,
            email=clean_email,
            password=hashed_password,
            role="employee",
            city=city,
            country=country
        )

        try:

           return await self.user_repository.create(
              db=db,
              obj=user
            )

        except Exception:

            await db.rollback()

            raise

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User | None:

        clean_email = email.strip().lower() if email else ""

        user = await self.user_repository.get_by_email(
            db=db,
            email=clean_email
        )

        if user is None or not getattr(user, "password", None):
            return None

        is_valid = self.verify_password(
            password,
            str(user.password)
        )

        if not is_valid:
            return None

        return user

    async def authenticate_or_create_google_user(
        self,
        db: AsyncSession,
        email: str,
        name: str,
        google_sub: str,
        city: Optional[str] = None,
        country: Optional[str] = None
    ) -> User:

        user = await self.user_repository.get_by_email(
            db=db,
            email=email
        )

        if user:
            if not getattr(user, "is_active", True):
                raise ValueError("Account is inactive")
            if (not getattr(user, "city", None) or not getattr(user, "country", None)) and (city or country):
                if city and not getattr(user, "city", None):
                    setattr(user, "city", city)
                if country and not getattr(user, "country", None):
                    setattr(user, "country", country)
                try:
                    await db.commit()
                    await db.refresh(user)
                except Exception:
                    await db.rollback()
            return user

        # First-time Google user creation
        new_user = User(
            name=name,
            email=email,
            password=None,
            role="employee",
            is_active=True,
            city=city,
            country=country
        )

        try:
            return await self.user_repository.create(
                db=db,
                obj=new_user
            )
        except Exception:
            await db.rollback()
            # Handle potential concurrent race condition on email uniqueness
            existing_user = await self.user_repository.get_by_email(
                db=db,
                email=email
            )
            if existing_user:
                if not getattr(existing_user, "is_active", True):
                    raise ValueError("Account is inactive")
                if (not getattr(existing_user, "city", None) or not getattr(existing_user, "country", None)) and (city or country):
                    if city and not getattr(existing_user, "city", None):
                        setattr(existing_user, "city", city)
                    if country and not getattr(existing_user, "country", None):
                        setattr(existing_user, "country", country)
                    try:
                        await db.commit()
                        await db.refresh(existing_user)
                    except Exception:
                        await db.rollback()
                return existing_user

            # If not an email collision, re-raise the true database exception
            raise