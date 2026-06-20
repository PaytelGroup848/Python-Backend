# app/modules/knowledge_bases/routes/knowledge_base_routes.py

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.knowledge_bases.schemas.knowledge_base_schema import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse
)

from app.modules.knowledge_bases.services.knowledge_base_service import (
    knowledge_base_service
)

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"]
)



@router.post(
    "/",
    response_model=KnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_knowledge_base(

    payload: KnowledgeBaseCreate,

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        knowledge_base = await (
            knowledge_base_service
            .create_knowledge_base(
                db=db,
                name=payload.name,
                code=payload.code,
                description=payload.description
            )
        )

        await db.commit()

        return knowledge_base

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[
        KnowledgeBaseResponse
    ]
)
async def list_knowledge_bases(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        knowledge_base_service
        .list_knowledge_bases(
            db
        )
    )

@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse
)
async def get_knowledge_base(
    knowledge_base_id: int,
    db: AsyncSession = Depends(get_db)
):

    knowledge_base = await (
        knowledge_base_service
        .get_knowledge_base(
            db,
            knowledge_base_id
        )
    )

    if not knowledge_base:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found"
        )

    return knowledge_base