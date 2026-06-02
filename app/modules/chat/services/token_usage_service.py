from app.models.token_usage import (
    TokenUsage
)

from app.modules.chat.repositories.token_usage_repository import (
    TokenUsageRepository
)


class TokenUsageService:

    def __init__(self):

        self.repository = (
            TokenUsageRepository()
        )

    async def log_usage(
        self,
        db,
        user_id: int,
        provider: str,
        model: str,
        usage: dict
    ):

        token_usage = TokenUsage(

            user_id=user_id,

            provider=provider,

            model=model,

            prompt_tokens=usage.get(
                "prompt_tokens",
                0
            ),

            completion_tokens=usage.get(
                "completion_tokens",
                0
            ),

            total_tokens=usage.get(
                "total_tokens",
                0
            ),
        )

        return await (
            self.repository.create(
                db=db,
                usage=token_usage
            )
        )
    
    async def get_total_tokens(
        self,
        db,
        user_id: int
    ):

        return await (
            self.repository
            .get_total_tokens(
                db,
                user_id
            )
        )


token_usage_service = (
    TokenUsageService()
)