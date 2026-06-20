from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.knowledge_bases.services.knowledge_base_upload_service import (
    knowledge_base_upload_service
)

from app.modules.knowledge_bases.schemas.knowledge_base_document_schema import (
    KnowledgeBaseDocumentResponse
)

from app.modules.knowledge_bases.services.knowledge_base_document_service import (
    knowledge_base_document_service
)

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Base Documents"]
)

@router.post(
    "/{knowledge_base_id}/documents",
    status_code=status.HTTP_201_CREATED
)
async def upload_document(

    knowledge_base_id: int,

    file: UploadFile = File(...),

    db: AsyncSession = Depends(
        get_db
    )
):

    try:

        return await (
            knowledge_base_upload_service
            .upload_document(
                db=db,
                knowledge_base_id=knowledge_base_id,
                file=file
            )
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get(
    "/{knowledge_base_id}/documents",
    response_model=list[
        KnowledgeBaseDocumentResponse
    ]
)
async def list_documents(

    knowledge_base_id: int,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        knowledge_base_document_service
        .list_documents(
            db=db,
            knowledge_base_id=
            knowledge_base_id
        )
    )

@router.get(
    "/documents/{document_id}",
    response_model=
    KnowledgeBaseDocumentResponse
)
async def get_document(

    document_id: int,

    db: AsyncSession = Depends(
        get_db
    )
):

    document = await (
        knowledge_base_document_service
        .get_document(
            db=db,
            document_id=document_id
        )
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document