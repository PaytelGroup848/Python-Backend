from fastapi import HTTPException

from app.modules.admin.repositories.user_repository import (
    UserRepository
)

from app.modules.chat.services.token_usage_service import (
    token_usage_service
)


class QuotaService:

    def __init__(self):

        self.user_repository = (
            UserRepository()
        )

    async def check_limit(
        self,
        db,
        user_id: int
    ):

        user = await (
            self.user_repository
            .get_by_id(
                db,
                user_id
            )
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        used_tokens = await (
            token_usage_service
            .get_total_tokens(
                db,
                user_id
            )
        )

        # Temporary Debug Log
        print(
            f"USER={user_id} "
            f"USED={used_tokens} "
            f"LIMIT={user.token_limit}"
        )

        if used_tokens >= user.token_limit:

            raise HTTPException(
                status_code=403,
                detail="Token limit exceeded. Please upgrade your plan."
            )

        return {
            "allowed": True,
            "used_tokens": used_tokens,
            "token_limit": user.token_limit,
            "remaining_tokens":
                user.token_limit - used_tokens
        }


quota_service = (
    QuotaService()
)