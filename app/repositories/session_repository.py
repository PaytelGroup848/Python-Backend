from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:

    async def create_session(
        self,
        db: AsyncSession,
        user_id,
        refresh_token: str
    ):

        session = Session(
            user_id=user_id,
            refresh_token=refresh_token
        )

        db.add(session)

        await db.commit()

        await db.refresh(session)

        return session

    async def get_by_refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ):

        result = await db.execute(
            select(Session).where(
                Session.refresh_token == refresh_token
            )
        )

        return result.scalar_one_or_none()

    async def delete_session(
        self,
        db: AsyncSession,
        session: Session
    ):

        await db.delete(session)

        await db.commit()