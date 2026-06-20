

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base_document import (
    KnowledgeBaseDocument
)


class KnowledgeBaseDocumentRepository:

    async def create(
        self,
        db: AsyncSession,
        document: KnowledgeBaseDocument
    ):
        db.add(document)

        await db.flush()

        await db.refresh(
            document
        )

        return document

    async def get_by_id(
        self,
        db: AsyncSession,
        document_id: int
    ):
        result = await db.execute(
            select(
                KnowledgeBaseDocument
            ).where(
                KnowledgeBaseDocument.id
                ==
                document_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_knowledge_base(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ):
        result = await db.execute(
            select(
                KnowledgeBaseDocument
            ).where(
                KnowledgeBaseDocument.knowledge_base_id
                ==
                knowledge_base_id
            )
        )

        return result.scalars().all()
    
    async def get_by_file_path(
        self,
        db: AsyncSession,
        file_path: str
    ):
        result = await db.execute(
            select(
                KnowledgeBaseDocument
            ).where(
                KnowledgeBaseDocument.file_path
                ==
                file_path
            )
        )

        return result.scalar_one_or_none()
    
    async def update(
        self,
        db: AsyncSession,
        document: KnowledgeBaseDocument
    ):
        await db.flush()

        await db.refresh(
            document
        )

        return document


knowledge_base_document_repository = (
    KnowledgeBaseDocumentRepository()
)