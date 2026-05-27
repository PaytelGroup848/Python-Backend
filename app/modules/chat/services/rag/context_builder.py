from app.core.config import (
    RAG_MAX_CONTEXT_CHARS
)


def build_context(
    results
) -> dict:

    context_parts = []

    sources = []

    seen_content = set()

    for r in results:

        if r.content not in seen_content:

            context_parts.append(
                r.content
            )

            seen_content.add(
                r.content
            )

        sources.append({
            "source_file": r.source_file,
            "page_number": r.page_number
        })

    context = "\n\n".join(
        context_parts
    )

    context = context[
        :RAG_MAX_CONTEXT_CHARS
    ]

    sources = sources[:10]

    return {
        "context": context,
        "sources": sources
    }