import hashlib
import secrets
from datetime import datetime

from sqlalchemy import select
from app.models.api_key import ApiKey
from app.models.user import User
from app.modules.api_keys.repositories.api_key_repository import ApiKeyRepository
from app.modules.usage.repositories.usage_repository import usage_repository


PLAN_LIMITS = {
    "free": 100000,
    "pro": 1000000,
    "enterprise": 10000000,
}


class ApiKeyService:

    def __init__(self):
        self.repository = ApiKeyRepository()

    async def create_api_key(
        self,
        db,
        user_id: int,
        name: str
    ):
        raw_key = f"sk_live_{secrets.token_hex(24)}"
        prefix = raw_key[:14]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        api_key = ApiKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            is_active=True
        )

        await self.repository.create(db, api_key)

        return {
            "id": api_key.id,
            "name": api_key.name,
            "key": raw_key,
            "prefix": prefix,
            "is_active": api_key.is_active,
            "created_at": api_key.created_at
        }

    async def get_user_keys(
        self,
        db,
        user_id: int
    ):
        keys = await self.repository.get_user_keys(db, user_id)

        items = []
        for k in keys:
            pref = getattr(k, "prefix", None) or "sk_live_"
            masked = f"{pref}••••••••••••••••"
            items.append({
                "id": k.id,
                "name": k.name,
                "prefix": getattr(k, "prefix", None),
                "key": masked,
                "is_active": bool(getattr(k, "is_active", True)),
                "created_at": k.created_at,
                "last_used_at": k.last_used_at
            })

        return {
            "api_keys": items
        }

    async def disable_api_key(
        self,
        db,
        user_id: int,
        api_key_id: int
    ):
        api_key = await self.repository.get_by_id(db, api_key_id)

        if not api_key or getattr(api_key, "user_id", None) != user_id:
            raise ValueError("API Key not found or unauthorized")

        await self.repository.disable_key(db, api_key)

        return {
            "message": "API Key disabled",
            "id": api_key.id,
            "is_active": getattr(api_key, "is_active", False)
        }

    async def delete_api_key(
        self,
        db,
        user_id: int,
        api_key_id: int
    ):
        api_key = await self.repository.get_by_id(db, api_key_id)

        if not api_key or getattr(api_key, "user_id", None) != user_id:
            raise ValueError("API Key not found or unauthorized")

        try:
            await self.repository.delete(db, api_key)
        except Exception:
            await db.rollback()
            api_key = await self.repository.get_by_id(db, api_key_id)
            if api_key:
                await self.repository.disable_key(db, api_key)

        return {
            "message": "API Key deleted",
            "id": api_key_id
        }

    async def get_user_api_key_usage(
        self,
        db,
        user_id: int
    ):
        total_tokens = int(await usage_repository.get_user_total_tokens(db, user_id) or 0)
        monthly_tokens = int(await usage_repository.get_user_monthly_tokens(db, user_id) or 0)

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        plan_name = "free"
        if user and hasattr(user, "plan_name") and user.plan_name:
            plan_name = str(user.plan_name).lower()

        token_limit = PLAN_LIMITS.get(plan_name, 100000)
        remaining = max(0, token_limit - monthly_tokens)
        cost = round((float(total_tokens) / 1000.0) * 0.002, 4)

        prompt_est = int(total_tokens * 0.6)
        comp_est = total_tokens - prompt_est

        return {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_est,
            "completion_tokens": comp_est,
            "monthly_tokens": monthly_tokens,
            "token_limit": token_limit,
            "remaining_tokens": remaining,
            "estimated_cost": cost,
            "plan_name": plan_name
        }


api_key_service = ApiKeyService()