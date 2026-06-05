import uuid

from app.models.api_request import (
    ApiRequest
)

from app.modules.api_requests.repositories.api_request_repository import (
    ApiRequestRepository
)


class ApiRequestService:

    def __init__(self):

        self.repository = (
            ApiRequestRepository()
        )

    async def log_request(
        self,
        db,
        user_id: int,
        api_key_id: int | None,
        model_name: str,
        provider: str,
        source: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: int,
        status_code: int
    ):

        request = ApiRequest(

            request_id=str(
                uuid.uuid4()
            ),

            user_id=user_id,

            api_key_id=api_key_id,

            model_name=model_name,

            provider=provider,

            source=source,

            prompt_tokens=prompt_tokens,

            completion_tokens=completion_tokens,

            total_tokens=total_tokens,

            latency_ms=latency_ms,

            status_code=status_code
        )

        return await (
            self.repository.create(
                db,
                request
            )
        )

    async def get_user_requests(
        self,
        db,
        user_id: int
    ):

        requests = await (
            self.repository
            .get_user_requests(
                db,
                user_id
            )
        )

        return {
            "requests": requests
        }


api_request_service = (
    ApiRequestService()
)