from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base_document import (
    KnowledgeBaseDocument
)

from app.modules.knowledge_bases.repositories.knowledge_base_repository import (
    knowledge_base_repository
)

from app.modules.knowledge_bases.repositories.knowledge_base_document_repository import (
    knowledge_base_document_repository
)


class KnowledgeBaseDocumentService:

    async def create_document(

        self,

        db: AsyncSession,

        knowledge_base_id: int,

        file_name: str,

        file_path: str,

        mime_type: str | None = None,

        file_size: int | None = None
    ):

        knowledge_base = (
            await knowledge_base_repository.get_by_id(
                db,
                knowledge_base_id
            )
        )

        if not knowledge_base:

            raise ValueError(
                "Knowledge base not found"
            )
        
        existing_document = (
            await knowledge_base_document_repository
            .get_by_file_path(
                db,
                file_path
            )
        )

        if existing_document:
            raise ValueError(
                "Document already exists"
            )

        document = (
            KnowledgeBaseDocument(

                knowledge_base_id=
                knowledge_base_id,

                file_name=
                file_name,

                file_path=
                file_path,

                mime_type=
                mime_type,

                file_size=
                file_size,

                status="pending"
            )
        )

        return await (
            knowledge_base_document_repository.create(
                db,
                document
            )
        )

    async def get_document(

        self,

        db: AsyncSession,

        document_id: int
    ):

        return await (
            knowledge_base_document_repository.get_by_id(
                db,
                document_id
            )
        )

    async def list_documents(

        self,

        db: AsyncSession,

        knowledge_base_id: int
    ):

        return await (
            knowledge_base_document_repository
            .list_by_knowledge_base(
                db,
                knowledge_base_id
            )
        )

    async def mark_processing(

        self,

        db: AsyncSession,

        document_id: int
    ):

        document = (
            await knowledge_base_document_repository
            .get_by_id(
                db,
                document_id
            )
        )

        if not document:

            raise ValueError(
                "Document not found"
            )

        document.status = "processing"

        return await (
            knowledge_base_document_repository
            .update(
                db,
                document
            )
        )

    async def mark_completed(

        self,

        db: AsyncSession,

        document_id: int
    ):

        document = (
            await knowledge_base_document_repository
            .get_by_id(
                db,
                document_id
            )
        )

        if not document:

            raise ValueError(
                "Document not found"
            )

        document.status = "completed"

        document.error_message = None

        return await (
            knowledge_base_document_repository
            .update(
                db,
                document
            )
        )

    async def mark_failed(

        self,

        db: AsyncSession,

        document_id: int,

        error_message: str
    ):

        document = (
            await knowledge_base_document_repository
            .get_by_id(
                db,
                document_id
            )
        )

        if not document:

            raise ValueError(
                "Document not found"
            )

        document.status = "failed"

        document.error_message = (
            error_message
        )

        return await (
            knowledge_base_document_repository
            .update(
                db,
                document
            )
        )


knowledge_base_document_service = (
    KnowledgeBaseDocumentService()
)