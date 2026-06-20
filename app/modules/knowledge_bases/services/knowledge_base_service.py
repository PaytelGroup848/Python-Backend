from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_base import (
    KnowledgeBase
)

from app.modules.knowledge_bases.repositories.knowledge_base_repository import (
    knowledge_base_repository
)


class KnowledgeBaseService:

    async def create_knowledge_base(
        self,
        db: AsyncSession,
        name: str,
        code: str,
        description: str | None = None
    ):
        
        code = code.strip().lower()

        name = name.strip()

        existing = (
            await knowledge_base_repository.get_by_code(
                db,
                code
            )
        )

        if existing:

            raise ValueError(
                f"Knowledge base '{code}' already exists"
            )

        knowledge_base = KnowledgeBase(
            name=name,
            code=code,
            description=description
        )

        return await (
            knowledge_base_repository.create(
                db,
                knowledge_base
            )
        )

    async def get_knowledge_base(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ):

        return await (
            knowledge_base_repository.get_by_id(
                db,
                knowledge_base_id
            )
        )

    async def get_by_code(
        self,
        db: AsyncSession,
        code: str
    ):

        return await (
            knowledge_base_repository.get_by_code(
                db,
                code
            )
        )

    async def list_knowledge_bases(
        self,
        db: AsyncSession
    ):

        return await (
            knowledge_base_repository.list_active(
                db
            )
        )

    async def deactivate_knowledge_base(
        self,
        db: AsyncSession,
        knowledge_base_id: int
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

        knowledge_base.is_active = False

        return await (
            knowledge_base_repository.update(
                db,
                knowledge_base
            )
        )


knowledge_base_service = (
    KnowledgeBaseService()
)