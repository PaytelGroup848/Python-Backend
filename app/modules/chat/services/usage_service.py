from app.db.redis_client import (
    redis_client
)


USER_PLANS = {

    "free": 10000,

    "pro": 100000,

    "enterprise": 1000000,
}


USER_PLAN_MAP = {

    "user1": "free",

    "user2": "pro",
}


class UsageService:

    async def track_usage(

        self,

        user_id: str,

        tokens: int,
    ) -> None:

        key = (
            f"usage:{user_id}"
        )

        current = (
            await redis_client.get(
                key
            )
        )

        current = (
            int(current)
            if current
            else 0
        )

        current += tokens

        await redis_client.setex(

            key,

            86400,

            current,
        )

    async def check_usage_limit(

        self,

        user_id: str,
    ) -> bool:

        plan = (
            USER_PLAN_MAP.get(
                user_id,
                "free",
            )
        )

        max_tokens = (
            USER_PLANS[plan]
        )

        key = (
            f"usage:{user_id}"
        )

        usage = (
            await redis_client.get(
                key
            )
        )

        if (
            usage
            and int(usage)
            >= max_tokens
        ):

            return False

        return True

    async def get_user_plan(
        self,
        user_id: str,
    ) -> str:

        return USER_PLAN_MAP.get(
            user_id,
            "free",
        )


usage_service = (
    UsageService()
)