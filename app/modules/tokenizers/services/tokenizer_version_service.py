from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.tokenizers.repositories.tokenizer_version_repository import (
    tokenizer_version_repository,
)


class TokenizerVersionService:

    async def list_by_tokenizer(
        self,
        db: AsyncSession,
        tokenizer_id: int,
    ):

        return await (
            tokenizer_version_repository
            .list_by_tokenizer(
                db=db,
                tokenizer_id=tokenizer_id,
            )
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        tokenizer_version_id: int,
    ):

        return await (
            tokenizer_version_repository
            .get_by_id(
                db=db,
                tokenizer_version_id=tokenizer_version_id,
            )
        )


tokenizer_version_service = (
    TokenizerVersionService()
)