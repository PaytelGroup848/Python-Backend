import re
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

    original_content: str | None = None,

    language: str = "en",

    is_translated: bool = False,

    source_file: str | None = None,

    page_number: int | None = None,

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


from app.modules.mini_ai.cache import get_kb_cache_version

RRF_K = 60


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

    kb_version = await get_kb_cache_version(knowledge_base_ids)

    cache_key = (

        f"semantic_search:"
        f"v{kb_version}:"
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

                d.department = :user_department
                OR d.department = 'general'
                OR d.department IS NULL
                OR :user_role = 'admin'
                OR :user_role = 'employee'
            )

        ORDER BY d.embedding <=> CAST(
            :embedding AS vector
        )

        LIMIT :limit
    """)

    # =========================
    # KEYWORD SEARCH SQL (PostgreSQL FTS BM25)
    # =========================

    keyword_sql = text("""

        SELECT
            d.id,
            d.content,
            d.source_file,
            d.page_number,

            (1.0 / (1.0 + ts_rank_cd(d.content_tsv, plainto_tsquery('simple', :raw_query)))) AS distance

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

            d.content_tsv @@ plainto_tsquery('simple', :raw_query)

            AND (
                d.department = :user_department
                OR d.department = 'general'
                OR d.department IS NULL
                OR :user_role = 'admin'
                OR :user_role = 'employee'
            )

        ORDER BY ts_rank_cd(d.content_tsv, plainto_tsquery('simple', :raw_query)) DESC

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
    # KEYWORD SEARCH (FTS)
    # =========================

    try:

        keyword_result = await asyncio.wait_for(

            db.execute(

                keyword_sql,

                {
                    "raw_query": query,

                    "limit": limit,

                    "user_department": user_department,

                    "knowledge_base_ids": knowledge_base_ids,

                    "user_role": user_role,
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
    # RECIPROCAL RANK FUSION (RRF)
    # =========================

    from typing import Any
    rrf_scores: dict[int, float] = {}
    combined_rows: dict[int, Any] = {}

    for rank, row in enumerate(vector_results, start=1):
        rrf_scores[row.id] = rrf_scores.get(row.id, 0.0) + 1.0 / (RRF_K + rank)
        combined_rows[row.id] = row

    for rank, row in enumerate(keyword_results, start=1):
        rrf_scores[row.id] = rrf_scores.get(row.id, 0.0) + 1.0 / (RRF_K + rank)
        if row.id not in combined_rows:
            combined_rows[row.id] = row

    ranked_ids = sorted(rrf_scores.keys(), key=lambda doc_id: rrf_scores[doc_id], reverse=True)
    final_results = [combined_rows[doc_id] for doc_id in ranked_ids[:limit]]

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


class DatasetSearchResult:
    def __init__(self, id, content, source_file, page_number, distance, dataset_name=None, domain=None):
        self.id = id
        self.content = content
        self.source_file = source_file
        self.page_number = page_number
        self.distance = distance
        self.dataset_name = dataset_name
        self.domain = domain


async def semantic_search_datasets(
    db: AsyncSession,
    query: str,
    domain: str | None = None,
    limit: int = 5,
) -> list[DatasetSearchResult]:
    query = query.strip().lower()
    if not query:
        return []

    try:
        query_embedding = await generate_embedding(query)
    except Exception as exc:
        logger.error(f"Failed to generate query embedding: {exc}")
        return []

    embedding_str = str(query_embedding)
    limit = min(max(1, limit), 20)

    try:
        if domain and domain.strip().lower() not in ["general", "all", "universal", "none"]:
            clean_domain = domain.strip().lower()
            query_sql = text("""
                SELECT 
                    dr.id,
                    dr.input_text AS content,
                    dr.metadata_json,
                    d.name AS dataset_name,
                    d.domain AS dataset_domain,
                    (dr.embedding <=> CAST(:emb AS vector)) AS distance
                FROM dataset_records dr
                JOIN datasets d ON d.id = dr.dataset_id
                WHERE dr.embedding IS NOT NULL
                  AND (LOWER(d.domain) = :domain OR LOWER(d.domain) LIKE :domain_like)
                ORDER BY dr.embedding <=> CAST(:emb AS vector) ASC
                LIMIT :limit
            """)
            params = {
                "emb": embedding_str,
                "domain": clean_domain,
                "domain_like": f"%{clean_domain}%",
                "limit": limit
            }
        else:
            query_sql = text("""
                SELECT 
                    dr.id,
                    dr.input_text AS content,
                    dr.metadata_json,
                    d.name AS dataset_name,
                    d.domain AS dataset_domain,
                    (dr.embedding <=> CAST(:emb AS vector)) AS distance
                FROM dataset_records dr
                JOIN datasets d ON d.id = dr.dataset_id
                WHERE dr.embedding IS NOT NULL
                ORDER BY dr.embedding <=> CAST(:emb AS vector) ASC
                LIMIT :limit
            """)
            params = {
                "emb": embedding_str,
                "limit": limit
            }

        res = await db.execute(query_sql, params)
        rows = res.fetchall()

        import json
        results = []
        for row in rows:
            meta = row.metadata_json or {}
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = {}

            source_file = meta.get("source_file") or row.dataset_name or "Dataset Document"
            page_number = meta.get("page_number")
            dist = float(row.distance) if row.distance is not None else 1.0

            results.append(
                DatasetSearchResult(
                    id=row.id,
                    content=row.content,
                    source_file=source_file,
                    page_number=page_number,
                    distance=dist,
                    dataset_name=row.dataset_name,
                    domain=row.dataset_domain
                )
            )

        logger.info(f"Dataset semantic search: domain={domain}, found={len(results)}")
        return results

    except Exception as e:
        logger.exception(f"Dataset semantic search failed: {e}")
        return []