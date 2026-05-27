from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy import select

from app.core.security import (
    verify_token
)

from app.db.redis_client import (
    redis_client
)

from app.db.database import (
    AsyncSessionLocal
)

from app.models.document import (
    Document
)

from app.services.document_translation_service import (
    translate_large_text
)

from app.schemas.translation import (
    TranslationRequest
)

router = APIRouter()


@router.post("/translate-document")
async def translate_document(

    req: TranslationRequest,

    user=Depends(
        verify_token
    )
):

    async with AsyncSessionLocal() as db:

        source_file = await redis_client.get(

            f"latest_pdf:{user['user_id']}"
        )

        if not source_file:

            return {
                "error":
                    "No uploaded document found"
            }

        result = await db.execute(

            select(Document)

            .where(
                Document.source_file
                ==
                source_file
            )

            .order_by(
                Document.page_number
            )
        )

        docs = result.scalars().all()

        if not docs:

            return {
                "error":
                    "Document not found"
            }

        full_text = "\n\n".join([

            d.original_content
            or d.content

            for d in docs
        ])

        translated = translate_large_text(

            full_text,

            req.target_language
        )

        return {

            "source_file":
                source_file,

            "target_language":
                req.target_language,

            "translated_text":
                translated
        }