
from app.core.config import settings


def build_context(
    results
) -> dict:

    context_parts = []

    sources = []

    seen_content = set()

    seen_sources = set()

    for r in results:

        content = (
            r.content or ""
        ).strip()

        if (
            content
            and
            content not in seen_content
        ):

            context_parts.append(
                content
            )

            seen_content.add(
                content
            )

        source_key = (
            r.source_file,
            r.page_number
        )

        if (
            source_key
            not in seen_sources
        ):

            sources.append({

                "source_file": (
                    r.source_file
                ),

                "page_number": (
                    r.page_number
                )
            })

            seen_sources.add(
                source_key
            )

    context = "\n\n".join(
        context_parts
    )

    context = context[
        :settings.RAG_MAX_CONTEXT_CHARS
    ]

    sources = sources[:10]

    return {
        "context": context,
        "sources": sources
    }

