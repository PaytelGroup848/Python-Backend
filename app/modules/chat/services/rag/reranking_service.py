import asyncio
import logging

from typing import Sequence

from app.shared.ai.reranker import (
    get_reranker
)

logger = logging.getLogger(__name__)


async def rerank_results(
    query: str,
    results: Sequence
) -> list:

    if not results:
        return []

    pairs = [
        (query, r.content)
        for r in results
        if getattr(r, "content", None)
    ]

    if not pairs:
        return list(results)

    try:

        reranker = get_reranker()

        scores = await asyncio.to_thread(

            reranker.predict,

            pairs
        )

        reranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [r[0] for r in reranked]

    except Exception as e:

        logger.exception(
            f"Reranking failed: {str(e)}"
        )

        return list(results)