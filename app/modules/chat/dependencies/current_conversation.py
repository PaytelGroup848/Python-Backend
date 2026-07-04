from fastapi import (
    Depends,
    HTTPException,
    Path,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.chat.models.conversation import (
    Conversation,
    ConversationStatus,
)

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository,
)

from app.modules.workspaces.models.workspace import (
    Workspace,
)

from app.modules.chat.dependencies.current_workspace import (
    get_current_workspace,
)


async def get_current_conversation(

    conversation_id: int = Path(...),

    workspace: Workspace = Depends(
        get_current_workspace
    ),

    db: AsyncSession = Depends(
        get_db
    ),

) -> Conversation:

    conversation = await conversation_repository.get_by_id(

        db=db,

        conversation_id=conversation_id,

    )

    if conversation is None:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Conversation not found",

        )

    if conversation.workspace_id != workspace.id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Conversation does not belong to this workspace",

        )

    if conversation.organization_id != workspace.organization_id:

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Conversation does not belong to your organization",

        )

    if conversation.status == ConversationStatus.DELETED:

        raise HTTPException(

            status_code=status.HTTP_410_GONE,

            detail="Conversation has been deleted",

        )

    return conversation