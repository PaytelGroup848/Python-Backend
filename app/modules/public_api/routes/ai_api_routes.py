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
    Depends,
    Request,
    HTTPException
)

from app.modules.public_api.schemas.ai_api_schema import (
    ChatCompletionRequest,
    ImageGenerationAPIRequest
)

from app.modules.api_keys.dependencies.api_key_auth import (
    validate_api_key
)


from fastapi import HTTPException

from app.modules.models.repositories.model_repository import (
    ModelRepository
)

from app.modules.providers.provider_registry import (
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
            messages,
            model=payload.model
        )
    )

    print(
        "PUBLIC API MODEL:",
        response.get("model")
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

            api_key_id=getattr(getattr(current_user, "current_api_key", None), "id", None),

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


@router.post(
    "/images/generations"
)
async def create_image_generation(
    payload: ImageGenerationAPIRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(validate_api_key),
):
    from app.services.image_generation_service import image_generation_service
    from app.services.image_providers.base import (
        ContentPolicyViolationError,
        ProviderAPIError,
        ProviderTimeoutError
    )

    if not payload.prompt or not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required.")

    user_id = current_user.id if hasattr(current_user, "id") else 1

    try:
        result = await image_generation_service.generate_and_persist(
            user_id=user_id,
            conversation_id=None,
            prompt=payload.prompt.strip(),
            aspect_ratio=payload.size or "1024x1024",
        )
    except ContentPolicyViolationError as cpv:
        raise HTTPException(status_code=400, detail=f"Content policy violation: {str(cpv)}")
    except ProviderTimeoutError as pto:
        raise HTTPException(status_code=504, detail=f"Image generation timeout: {str(pto)}")
    except ProviderAPIError as pae:
        raise HTTPException(status_code=502, detail=f"Image generation provider error: {str(pae)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(exc)}")

    base_url = str(request.base_url).rstrip("/")
    file_url = result["file_url"]
    full_url = f"{base_url}{file_url}" if not file_url.startswith("http") else file_url

    return {
        "created": int(time.time()),
        "data": [
            {
                "url": full_url,
                "revised_prompt": result.get("enhanced_prompt") or payload.prompt,
            }
        ]
    }