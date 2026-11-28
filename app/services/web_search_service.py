from __future__ import annotations

import logging
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger("web_search_service")


def _sanitize_query(query: str) -> str:
    clean_q = re.sub(
        r"\b(search\s+(the\s+)?web|search\s+online|search\s+internet|google\s+this|browse\s+the\s+web|please|find\s+out)\b",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip()
    clean_q = clean_q.split("\n")[0].strip().strip("\"'*")
    if len(clean_q) > 120:
        clean_q = clean_q[:120].strip()
    return clean_q or query.strip()[:100]


def _extract_domain(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return re.sub(r"^www\.", "", host, flags=re.IGNORECASE)
    except Exception:
        return ""


def _build_favicon_url(domain: str) -> str:
    if not domain:
        return ""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"


class WebSearchService:
    """Executes resilient live web + image search with structured Perplexity-style metadata."""

    @staticmethod
    def search_with_images(
        query: str,
        max_results: int = 8,
        max_images: int = 8,
    ) -> Dict[str, List[Dict[str, Any]]]:
        clean_q = _sanitize_query(query)
        sources: List[Dict[str, Any]] = []
        images: List[Dict[str, Any]] = []

        try:
            from ddgs import DDGS

            with DDGS() as ddgs:
                try:
                    raw_results = list(ddgs.text(clean_q, max_results=max_results))
                    for item in raw_results:
                        title = (item.get("title") or "Web Result").strip()
                        href = (item.get("href") or "").strip()
                        body = (item.get("body") or "").strip()
                        if not href or not (title or body):
                            continue
                        idx = len(sources) + 1
                        domain = _extract_domain(href)
                        sources.append({
                            "id": idx,
                            "index": idx,
                            "title": title,
                            "url": href,
                            "domain": domain,
                            "snippet": body,
                            "favicon": _build_favicon_url(domain),
                        })
                except Exception as text_exc:
                    logger.warning(f"Live web text search error for '{clean_q}': {text_exc}")

                if max_images > 0:
                    try:
                        raw_images = list(ddgs.images(clean_q, max_results=max_images))
                        for img in raw_images:
                            img_url = (img.get("image") or "").strip()
                            thumb_url = (img.get("thumbnail") or img_url).strip()
                            src_url = (img.get("url") or "").strip()
                            title = (img.get("title") or "").strip()
                            if img_url.startswith(("http://", "https://")):
                                images.append({
                                    "title": title,
                                    "url": img_url,
                                    "thumbnail": thumb_url,
                                    "source_url": src_url,
                                    "domain": _extract_domain(src_url or img_url),
                                })
                    except Exception as img_exc:
                        logger.warning(f"Live web image search error for '{clean_q}': {img_exc}")
        except Exception as exc:
            logger.warning(f"WebSearchService initialization error for '{clean_q}': {exc}")

        return {"sources": sources, "images": images}

    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Backward-compatible text search returning structured source dictionaries."""
        return WebSearchService.search_with_images(
            query=query,
            max_results=max_results,
            max_images=0,
        )["sources"]

    @staticmethod
    def format_search_context(results: List[Dict[str, Any]]) -> str:
        """Formats search results into structured prompt context with numbered citations [1], [2]..."""
        if not results:
            return ""

        lines = ["=== REAL-TIME LIVE WEB SEARCH RESULTS ==="]
        for i, res in enumerate(results, start=1):
            lines.append(f"[{i}] {res['title']}")
            lines.append(f"URL: {res['url']}")
            lines.append(f"Summary: {res['snippet']}\n")
        lines.append("=== END OF WEB SEARCH RESULTS ===")
        lines.append(
            "INSTRUCTIONS: Use the real-time web search results above to answer the user question accurately. "
            "Cite your claims with inline numbers like [1], [2] corresponding to the sources above."
        )
        return "\n".join(lines)


web_search_service = WebSearchService()

__all__ = ["WebSearchService", "web_search_service"]
