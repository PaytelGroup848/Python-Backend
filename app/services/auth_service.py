from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository

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

        return pwd_context.verify(
            password,
            hashed_password
        )

    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User:

        existing_user = await self.user_repository.get_by_email(
            db=db,
            email=email
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        hashed_password = self.hash_password(password)

        user = User(
            email=email,
            password=hashed_password,
            role="employee"
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

        user = await self.user_repository.get_by_email(
            db=db,
            email=email
        )

        if not user:
            return None

        is_valid = self.verify_password(
            password,
            user.password
        )

        if not is_valid:
            return None

        return user