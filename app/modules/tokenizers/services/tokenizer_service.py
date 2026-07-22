from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.tokenizers.repositories.tokenizer_repository import (
    tokenizer_repository,
)


class TokenizerService:

    async def list_tokenizers(
        self,
        db: AsyncSession,
    ):

        return await (
            tokenizer_repository
            .list_tokenizers(
                db=db,
            )
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        tokenizer_id: int,
    ):

        return await (
            tokenizer_repository
            .get_by_id(
                db=db,
                tokenizer_id=tokenizer_id,
            )
        )


tokenizer_service = (
    TokenizerService()
)