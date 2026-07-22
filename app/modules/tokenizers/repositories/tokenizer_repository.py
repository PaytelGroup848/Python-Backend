from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.tokenizers.models.tokenizer import (
    Tokenizer,
)


class TokenizerRepository:

    async def list_tokenizers(

        self,

        db: AsyncSession,

    ):

        result = await db.execute(

            select(
                Tokenizer
            )

            .order_by(
                Tokenizer.display_name
            )

        )

        return result.scalars().all()

    async def get_by_id(

        self,

        db: AsyncSession,

        tokenizer_id: int,

    ):

        result = await db.execute(

            select(
                Tokenizer
            )

            .where(
                Tokenizer.id
                ==
                tokenizer_id
            )

        )

        return result.scalar_one_or_none()


tokenizer_repository = (
    TokenizerRepository()
)