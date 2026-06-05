import uuid

import time

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.api_requests.services.api_request_service import (
    api_request_service
)

from fastapi import (
    APIRouter,
    Depends
)

from app.modules.public_api.schemas.ai_api_schema import (
    ChatCompletionRequest
)

from app.modules.api_keys.dependencies.api_key_auth import (
    validate_api_key
)


from fastapi import HTTPException

from app.modules.models.repositories.model_repository import (
    ModelRepository
)

from app.modules.chat.providers.provider_registry import (
    provider_registry
)

from app.modules.models.services.model_service import (
    model_service
)


router = APIRouter(

    prefix="/v1",

    tags=["Public AI API"]
)

model_repository = (
    ModelRepository()
)


@router.post(
    "/chat/completions"
)
async def chat_completions(

    payload: ChatCompletionRequest,

    db: AsyncSession = Depends(
        get_db
    ),

    current_user = Depends(
        validate_api_key
    )
):

    last_message = (
        payload.messages[-1]
        .content
    )

    session_id = str(
        uuid.uuid4()
    )

    start_time = time.time()

    model = await (
        model_repository.get_by_name(
            db,
            payload.model
        )
    )

    if not model:

        raise HTTPException(

            status_code=404,

            detail="Model not found"
        )

    if not model.is_active:

        raise HTTPException(

            status_code=400,

            detail="Model disabled"
        )

    provider = (
        model.provider
    )

    provider_instance = (
        provider_registry.get(
            provider
        )
    )

    if not provider_instance:

        raise HTTPException(

            status_code=500,

            detail=(
                f"Provider "
                f"{provider} "
                f"not configured"
            )
        )

    messages = [

        {

            "role": "user",

            "content": last_message
        }
    ]

    response = await (
        provider_instance.generate(
            messages
        )
    )

    usage = response.get(
        "usage",
        {}
    )

    prompt_tokens = usage.get(
        "prompt_tokens",
        0
    )

    completion_tokens = usage.get(
        "completion_tokens",
        0
    )

    total_tokens = usage.get(
        "total_tokens",
        0
    )

    print(
        "TOKEN USAGE:",
        usage
    )


    latency_ms = int(
        (
            time.time()
            - start_time
        ) * 1000
    )

    await (
        api_request_service
        .log_request(

            db=db,

            user_id=current_user.id,

            api_key_id=None,

            model_name=response.get(
                "model",
                payload.model
            ),

            provider=provider,

            source="api",

            prompt_tokens=prompt_tokens,

            completion_tokens=completion_tokens,

            total_tokens=total_tokens,

            latency_ms=latency_ms,

            status_code=200
        )
    )

    return {

        "id":
            str(uuid.uuid4()),

        "object":
            "chat.completion",

        "model":
            payload.model,

        "choices": [

            {

                "index": 0,

                "message": {

                    "role":
                        "assistant",

                    "content":
                        response.get(
                            "response",
                            ""
                        )
                },

                "finish_reason":
                    "stop"
            }
        ]
    }


@router.get(
    "/models"
)
async def get_models(

    db: AsyncSession = Depends(
        get_db
    )
):

    models = await (
        model_service
        .get_active_models(
            db
        )
    )

    return {

        "object": "list",

        "data": [

            {

                "id":
                    model.model_name,

                "provider":
                    model.provider

            }

            for model in models
        ]
    }