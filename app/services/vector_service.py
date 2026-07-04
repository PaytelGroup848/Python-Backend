import asyncio
import logging

from typing import List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.document import (
    Document
)

from app.modules.retrieval_runtime.services.embedding_service import (
    generate_embedding,
)

from app.shared.cache.cache_service import (
    cache_service
)

logger = logging.getLogger(__name__)


async def store_document(

    db: AsyncSession,

    embedding: List[float],

    content: str,

    knowledge_base_document_id: int,

    original_content: str = None,

    language: str = "en",

    is_translated: bool = False,

    source_file: str = None,

    page_number: int = None,

    department: str = "general",

    access_level: str = "internal",

    uploaded_by: int = 0
):

    doc = Document(

        content=content,

        knowledge_base_document_id= 
            knowledge_base_document_id,

        original_content=original_content,

        language=language,

        is_translated=is_translated,

        embedding=embedding,

        source_file=source_file,

        page_number=page_number,

        department=department,

        access_level=access_level,

        uploaded_by=uploaded_by
    )

    db.add(doc)

    return doc


async def semantic_search(

    db: AsyncSession,

    query: str,

    knowledge_base_ids: list[int],

    user_department: str,

    user_role: str,

    limit: int = 5,
):

    # =========================
    # QUERY NORMALIZATION
    # =========================

    query = query.strip().lower()

    if not query:

        return []

    if len(query) > 1000:

        logger.warning(
            "Search query too large"
        )

        return []

    limit = min(limit, 20)

    # =========================
    # CACHE KEY
    # =========================

    cache_key = (

        f"semantic_search:"
        f"{query}:"
        f"{sorted(knowledge_base_ids)}:"
        f"{user_department}:"
        f"{user_role}:"
        f"{limit}"
    )

    # =========================
    # CACHE CHECK
    # =========================

    cached_result = await (
        cache_service.get(
            cache_key
        )
    )

    if cached_result:

        logger.info(
            "Semantic search cache hit"
        )

        return cached_result

    # =========================
    # GENERATE EMBEDDING
    # =========================

    try:

        embedding = await asyncio.wait_for(

            generate_embedding(query),

            timeout=30,
        )

        embedding_str = (

            "[" +

            ",".join(
                map(
                    str,
                    embedding
                )
            )

            + "]"
        )

    except Exception as e:

        logger.exception(

            f"Embedding generation failed: "
            f"{str(e)}"
        )

        return []

    # =========================
    # VECTOR SEARCH SQL
    # =========================

    vector_sql = text("""

        SELECT
            d.id,
            d.content,
            d.source_file,
            d.page_number,

            d.embedding <=> CAST(
                :embedding AS vector
            ) AS distance

        FROM documents d

        JOIN knowledge_base_documents kbd
            ON d.knowledge_base_document_id = kbd.id

        WHERE

            kbd.knowledge_base_id = ANY(:knowledge_base_ids)

            AND

            (

                d.department =
                :user_department

                OR

                :user_role = 'admin'
            )

        ORDER BY d.embedding <=> CAST(
            :embedding AS vector
        )

        LIMIT :limit
    """)

    # =========================
    # KEYWORD SEARCH SQL
    # =========================

    keyword_sql = text("""

        SELECT
            d.id,
            d.content,
            d.source_file,
            d.page_number,

            0.0 AS distance

        FROM documents d

        JOIN knowledge_base_documents kbd
            ON d.knowledge_base_document_id = kbd.id

        WHERE

            kbd.knowledge_base_id IN (
                SELECT UNNEST(
                    CAST(
                        :knowledge_base_ids
                        AS int[]
                    )
                )
            )

            AND

            d.content ILIKE :keyword

            AND (

                d.department =
                :user_department

                OR

                :user_role = 'admin'
            
        )

        LIMIT :limit
    """)

    # =========================
    # VECTOR SEARCH
    # =========================

    try:

        vector_result = await asyncio.wait_for(

            db.execute(

                vector_sql,

                {
                    "embedding": embedding_str,

                    "limit": limit,

                    "user_department":
                    user_department,

                    "knowledge_base_ids":
                      knowledge_base_ids,

                    "user_role":
                    user_role
                }
            ),

            timeout=30,
        )

        vector_results = (
            vector_result.fetchall()
        )

    except Exception as e:

        logger.exception(

            f"Vector search failed: "
            f"{str(e)}"
        )

        vector_results = []

    # =========================
    # KEYWORD SEARCH
    # =========================

    try:

        keyword_result = await asyncio.wait_for(

            db.execute(

                keyword_sql,

                {
                    "keyword":
                    f"%{query}%",

                    "limit":
                    limit,

                    "user_department":
                    user_department,

                    "knowledge_base_ids":
                        knowledge_base_ids,

                    "user_role":
                    user_role
                }
            ),

            timeout=30,
        )

        keyword_results = (
            keyword_result.fetchall()
        )

    except Exception as e:

        logger.exception(

            f"Keyword search failed: "
            f"{str(e)}"
        )

        keyword_results = []

    # =========================
    # MERGE RESULTS
    # =========================

    combined = {}

    for row in vector_results:

        combined[row.id] = row

    for row in keyword_results:

        combined[row.id] = row

    final_results = list(
        combined.values()
    )

    # =========================
    # CACHE RESULTS
    # =========================

    try:

        await cache_service.set(

            cache_key,

            [
                dict(row._mapping)
                for row in final_results
            ],

            ttl=300,
        )

    except Exception as e:

        logger.warning(

            f"Cache set failed: "
            f"{str(e)}"
        )

    # =========================
    # LOGGING
    # =========================

    logger.info(

        f"Semantic search completed "

        f"vector={len(vector_results)} "

        f"keyword={len(keyword_results)} "

        f"combined={len(final_results)}"
    )

    return final_results