import hashlib

from datetime import datetime

from sqlalchemy import select

from app.models.api_key import ApiKey

from app.models.user import User


class ApiKeyAuthService:

    async def validate_key(
        self,
        db,
        api_key: str
    ):

        key_hash = hashlib.sha256(
            api_key.encode()
        ).hexdigest()

        

        result = await db.execute(

            select(ApiKey)

            .where(
                ApiKey.key_hash == key_hash
            )
        )

        key_record = (
            result.scalar_one_or_none()
        )

        

        if not key_record:

            return None

        if not key_record.is_active:

            return None
        key_record.last_used_at = (
            datetime.utcnow()
        )

        await db.commit()

        result = await db.execute(

            select(User)

            .where(
                User.id ==
                key_record.user_id
            )
        )

        user = (
            result.scalar_one_or_none()
        )

       

        if not user:

            return None

        if not user.is_active:
            return None

        user.current_api_key = key_record

        return user


api_key_auth_service = (
    ApiKeyAuthService()
)