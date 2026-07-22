from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.tokenizers.models.tokenizer_version import (
    TokenizerVersion,
)


class TokenizerVersionRepository:

    async def list_by_tokenizer(

        self,

        db: AsyncSession,

        tokenizer_id: int,

    ):

        result = await db.execute(

            select(
                TokenizerVersion
            )

            .where(
                TokenizerVersion.tokenizer_id
                ==
                tokenizer_id
            )

            .order_by(
                TokenizerVersion.created_at.desc()
            )

        )

        return result.scalars().all()

    async def get_by_id(

        self,

        db: AsyncSession,

        tokenizer_version_id: int,

    ):

        result = await db.execute(

            select(
                TokenizerVersion
            )

            .where(
                TokenizerVersion.id
                ==
                tokenizer_version_id
            )

        )

        return result.scalar_one_or_none()


tokenizer_version_repository = (
    TokenizerVersionRepository()
)