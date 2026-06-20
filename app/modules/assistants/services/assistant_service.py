from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import (
    Assistant
)

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)


class AssistantService:

    async def create_assistant(
        self,
        db: AsyncSession,
        name: str,
        code: str,
        description: str | None = None,
        system_prompt: str | None = None
    ):

        name = name.strip()

        code = code.strip().lower()

        existing = (
            await assistant_repository.get_by_code(
                db,
                code
            )
        )

        if existing:

            raise ValueError(
                f"Assistant '{code}' already exists"
            )

        assistant = Assistant(
            name=name,
            code=code,
            description=description,
            system_prompt=system_prompt
        )

        return await (
            assistant_repository.create(
                db,
                assistant
            )
        )

    async def get_assistant(
        self,
        db: AsyncSession,
        assistant_id: int
    ):

        return await (
            assistant_repository.get_by_id(
                db,
                assistant_id
            )
        )

    async def get_by_code(
        self,
        db: AsyncSession,
        code: str
    ):

        return await (
            assistant_repository.get_by_code(
                db,
                code
            )
        )

    async def list_assistants(
        self,
        db: AsyncSession
    ):

        return await (
            assistant_repository.list_active(
                db
            )
        )

    async def deactivate_assistant(
        self,
        db: AsyncSession,
        assistant_id: int
    ):

        assistant = (
            await assistant_repository.get_by_id(
                db,
                assistant_id
            )
        )

        if not assistant:

            raise ValueError(
                "Assistant not found"
            )

        assistant.is_active = False

        return await (
            assistant_repository.update(
                db,
                assistant
            )
        )


assistant_service = (
    AssistantService()
)