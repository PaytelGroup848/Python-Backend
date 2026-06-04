import hashlib
import secrets

from app.models.api_key import ApiKey

from app.modules.api_keys.repositories.api_key_repository import (
    ApiKeyRepository
)


class ApiKeyService:

    def __init__(self):

        self.repository = (
            ApiKeyRepository()
        )

    async def create_api_key(
        self,
        db,
        user_id: int,
        name: str
    ):

        raw_key = (
            f"sk_live_{secrets.token_hex(32)}"
        )

        key_hash = hashlib.sha256(
            raw_key.encode()
        ).hexdigest()

        api_key = ApiKey(

            user_id=user_id,

            name=name,

            key_hash=key_hash
        )

        await (
            self.repository.create(
                db,
                api_key
            )
        )

        return {

            "id": api_key.id,

            "name": api_key.name,

            "key": raw_key,

            "is_active": api_key.is_active,

            "created_at": api_key.created_at
        }

    async def get_user_keys(
        self,
        db,
        user_id: int
    ):

        keys = await (
            self.repository
            .get_user_keys(
                db,
                user_id
            )
        )

        return {
            "api_keys": keys
        }
    
    async def disable_api_key(
        self,
        db,
        api_key_id: int
    ):

        api_key = await (
            self.repository
            .get_by_id(
                db,
                api_key_id
            )
        )

        if not api_key:

            raise ValueError(
                "API Key not found"
            )

        await (
            self.repository
            .disable_key(
                db,
                api_key
            )
        )

        return {

            "message":
                "API Key disabled",

            "id":
                api_key.id,

            "is_active":
                api_key.is_active
        }
    
    async def enable_api_key(
        self,
        db,
        api_key_id: int
    ):

        api_key = await (
            self.repository
            .get_by_id(
                db,
                api_key_id
            )
        )

        if not api_key:

            raise ValueError(
                "API Key not found"
            )

        await (
            self.repository
            .enable_key(
                db,
                api_key
            )
        )

        return {

            "message":
                "API Key enabled",

            "id":
                api_key.id,

            "is_active":
                api_key.is_active
        }


api_key_service = (
    ApiKeyService()
)