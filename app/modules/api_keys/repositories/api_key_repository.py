from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey


class ApiKeyRepository:

    async def create(
        self,
        db: AsyncSession,
        api_key: ApiKey
    ):

        db.add(api_key)

        await db.commit()

        await db.refresh(api_key)

        return api_key

    async def get_user_keys(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(ApiKey)

            .where(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True
            )
            .order_by(ApiKey.id.desc())
        )

        return result.scalars().all()

    async def get_by_id(
        self,
        db: AsyncSession,
        api_key_id: int
    ):

        result = await db.execute(

            select(ApiKey)

            .where(
                ApiKey.id == api_key_id
            )
        )

        return result.scalar_one_or_none()
    
    async def enable_key(
        self,
        db: AsyncSession,
        api_key: ApiKey
    ):

        setattr(api_key, "is_active", True)

        await db.commit()

        await db.refresh(api_key)

        return api_key

    async def disable_key(
        self,
        db: AsyncSession,
        api_key: ApiKey
    ):

        setattr(api_key, "is_active", False)

        await db.commit()

        await db.refresh(api_key)

        return api_key

    async def delete(
        self,
        db: AsyncSession,
        api_key: ApiKey
    ):

        await db.delete(api_key)

        await db.commit()

        return True