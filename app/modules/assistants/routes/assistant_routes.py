from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.assistants.schemas.assistant_schema import (
    AssistantCreate,
    AssistantResponse
)

from app.modules.assistants.services.assistant_service import (
    assistant_service
)

router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"]
)


@router.post(
    "/",
    response_model=AssistantResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_assistant(

    payload: AssistantCreate,

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        assistant = await (
            assistant_service
            .create_assistant(
                db=db,
                name=payload.name,
                code=payload.code,
                description=payload.description,
                system_prompt=payload.system_prompt
            )
        )

        await db.commit()

        return assistant

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[
        AssistantResponse
    ]
)
@router.get(
    "/",
    response_model=list[
        AssistantResponse
    ]
)
async def list_assistants(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        assistant_service
        .list_assistants(
            db
        )
    )


@router.get(
    "/{assistant_id}",
    response_model=AssistantResponse
)
async def get_assistant(

    assistant_id: int,

    db: AsyncSession = Depends(
        get_db
    )
):

    assistant = await (
        assistant_service
        .get_assistant(
            db,
            assistant_id
        )
    )

    if not assistant:

        raise HTTPException(
            status_code=404,
            detail="Assistant not found"
        )

    return assistant