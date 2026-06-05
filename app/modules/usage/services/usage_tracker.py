# app/modules/usage/services/usage_tracker.py

from app.modules.api_requests.services.api_request_service import (
    api_request_service
)


class UsageTracker:

    async def track(
        self,
        db,
        user_id,
        api_key_id,
        model_name,
        provider,
        source,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        latency_ms,
        status_code=200
    ):
        
        print(
            "USAGE TRACKER CALLED:",
            source,
            provider,
            model_name,
            total_tokens
        )

        await (
            api_request_service
            .log_request(

                db=db,

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
        )

        print(
            "USAGE TRACKER SAVED"
        )


usage_tracker = UsageTracker()