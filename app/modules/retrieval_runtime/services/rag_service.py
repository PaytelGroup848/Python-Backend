import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.vector_service import semantic_search, semantic_search_datasets
from app.modules.retrieval_runtime.services.reranking_service import rerank_results
from app.modules.retrieval_runtime.services.context_builder import build_context
from app.modules.assistants.services.assistant_resolver_service import assistant_resolver_service

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

    assistant = None
    assistant_code = ""
    assistant_name = ""
    knowledge_base_ids = []

    if assistant_id is not None:
        try:
            assistant = await (
                assistant_resolver_service
                .resolve_assistant(
                    db=db,
                    assistant_id=assistant_id
                )
            )
            if isinstance(assistant, dict):
                knowledge_base_ids = assistant.get("knowledge_base_ids", [])
                assistant_code = assistant.get("assistant_code") or assistant.get("code") or ""
                assistant_name = assistant.get("assistant_name") or assistant.get("name") or ""
            elif assistant is not None:
                knowledge_base_ids = getattr(assistant, "knowledge_base_ids", [])
                assistant_code = getattr(assistant, "assistant_code", getattr(assistant, "code", ""))
                assistant_name = getattr(assistant, "assistant_name", getattr(assistant, "name", ""))
        except Exception as err:
            logger.warning(f"Could not resolve assistant {assistant_id}: {err}")

    # Map assistant code/name to domain
    code_lower = str(assistant_code).lower()
    name_lower = str(assistant_name).lower()

    if "law" in code_lower or "law" in name_lower or "legal" in code_lower:
        target_domain = "legal"
    elif "astro" in code_lower or "astro" in name_lower:
        target_domain = "astrology"
    elif "med" in code_lower or "health" in name_lower or "clinic" in code_lower:
        target_domain = "medical"
    elif "code" in code_lower or "coder" in code_lower:
        target_domain = "code"
    else:
        target_domain = "general"

    logger.info(f"Retrieving context for assistant_id={assistant_id}, code={assistant_code}, domain={target_domain}")

    # 1. Search domain-specific dataset records
    results = []
    try:
        dataset_results = await semantic_search_datasets(
            db=db,
            query=query,
            domain=target_domain,
            limit=top_k
        )
        if dataset_results:
            results = list(dataset_results)
    except Exception as exc:
        logger.warning(f"Failed searching datasets: {exc}")

    # 2. If no dataset results and knowledge base attached, search knowledge bases
    if not results and knowledge_base_ids:
        try:
            kb_results = await asyncio.wait_for(
                semantic_search(
                    db=db,
                    query=query,
                    knowledge_base_ids=knowledge_base_ids,
                    user_department=user_department,
                    user_role=user_role,
                    limit=top_k
                ),
                timeout=30,
            )
            if kb_results:
                results = list(kb_results)
        except Exception as exc:
            logger.warning(f"Failed searching knowledge bases: {exc}")

    if not results:
        return {
            "context": "",
            "sources": [],
            "needs_general_knowledge": True,
            "message": f"No {target_domain} domain information found in datasets."
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