from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.admin.repositories.admin_repository import (
    AdminRepository
)


class AdminService:

    def __init__(self):

        self.repository = (
            AdminRepository()
        )

    async def get_dashboard(
        self,
        db: AsyncSession,
    ):

        return await (
            self.repository
            .get_dashboard_metrics(db)
        )