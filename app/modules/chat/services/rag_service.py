import logging
import asyncio

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.core.config import (
    settings
)

from app.services.vector_service import (
    semantic_search
)

from app.modules.chat.services.rag.reranking_service import (
    rerank_results
)

from app.modules.chat.services.rag.context_builder import (
    build_context
)

from app.modules.assistants.services.assistant_resolver_service import (
    assistant_resolver_service
)

logger = logging.getLogger(__name__)


# -----------------------------
# TEXT CLEANING
# -----------------------------

def clean_text(
    text: str
) -> str:

    if not text:
        return ""

    return (
        text
        .replace("\x00", "")
        .replace("\r", " ")
        .strip()
    )


# -----------------------------
# BUILD RAG CONTEXT
# -----------------------------

async def retrieve_context(
    db: AsyncSession,
    query: str,
    assistant_id: int,
    user_department: str,
    user_role: str,
    top_k: int = 10
) -> dict:

    if not query.strip():

        return {
            "context": "",
            "sources": []
        }

    assistant = await (
        assistant_resolver_service
        .resolve_assistant(
            db=db,
            assistant_id=assistant_id
        )
    )

    knowledge_base_ids = (
        assistant["knowledge_base_ids"]
    )

    if not knowledge_base_ids:

        return {

            "context": "",

            "sources": [],

            "needs_general_knowledge": True,

            "message": (
                "No knowledge base "
                "is attached to "
                "this assistant."
            )
        }

    results = await asyncio.wait_for(

        semantic_search(

            db=db,

            query=query,

            knowledge_base_ids=knowledge_base_ids,

            user_department=
                user_department,

            user_role=
                user_role,

            limit=top_k
        ),

        timeout=30,
    )

    if not results:

        return {

            "context": "",

            "sources": [],

            "needs_general_knowledge": True,

            "message": (
                "I could not find "
                "relevant information "
                "in the uploaded "
                "documents."
            )
        }

    results = await rerank_results(
        query,
        results
    )

    results = results[:top_k]

    logger.info(
        f"RAG results count: "
        f"{len(results)}"
    )

    for r in results:

        logger.info(
            f"RAG source="
            f"{r.source_file} "
            f"distance="
            f"{getattr(r, 'distance', None)}"
        )

    best_result = results[0]

    distance = getattr(
        best_result,
        "distance",
        1.0
    )

    if (
        distance >
        settings.RAG_SIMILARITY_THRESHOLD
    ):

        return {

            "context": "",

            "sources": [],

            "needs_general_knowledge": True,

            "message": (
                "I could not find "
                "relevant information "
                "in the uploaded "
                "documents."
            )
        }

    return build_context(
        results
    )