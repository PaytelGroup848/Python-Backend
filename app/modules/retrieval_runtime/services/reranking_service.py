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
    
    MAX_RERANK_RESULTS = 50

    results = list(
        results
    )[
        :MAX_RERANK_RESULTS
    ]

    pairs = []

    for r in results:

        if isinstance(r, dict):

            content = r.get("content")

        else:

            content = getattr(
                r,
                "content",
                None
            )

        if content:

            pairs.append(
                (
                    query,
                    content
                )
            )

    if not pairs:
        return list(results)

    try:

        reranker = get_reranker()

        scores = await asyncio.to_thread(

            reranker.predict,

            pairs
        )

        if len(scores) != len(results):

            logger.warning(

                "Reranker score mismatch "

                f"results={len(results)} "

                f"scores={len(scores)}"
            )

            return list(results)

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