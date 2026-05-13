from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):

    def __init__(self):
        super().__init__(Document)

    async def get_by_department(
        self,
        db: AsyncSession,
        department: str
    ):

        result = await db.execute(
            select(Document).where(
                Document.department == department
            )
        )

        return result.scalars().all()