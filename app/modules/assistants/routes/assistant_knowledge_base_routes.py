from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.assistants.schemas.assistant_knowledge_base_schema import (
    AssistantKnowledgeBaseCreate,
    AssistantKnowledgeBaseResponse
)

from app.modules.assistants.services.assistant_knowledge_base_service import (
    assistant_knowledge_base_service
)

router = APIRouter(
    prefix="/assistants",
    tags=["Assistant Knowledge Bases"]
)


@router.post(
    "/{assistant_id}/knowledge-bases",
    response_model=AssistantKnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_mapping(

    assistant_id: int,

    payload: AssistantKnowledgeBaseCreate,

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        mapping = await (
            assistant_knowledge_base_service
            .create_mapping(
                db=db,
                assistant_id=assistant_id,
                knowledge_base_id=
                payload.knowledge_base_id
            )
        )

        await db.commit()

        return mapping

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{assistant_id}/knowledge-bases",
    response_model=list[
        AssistantKnowledgeBaseResponse
    ]
)
async def list_assistant_knowledge_bases(

    assistant_id: int,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        assistant_knowledge_base_service
        .list_assistant_knowledge_bases(
            db=db,
            assistant_id=assistant_id
        )
    )