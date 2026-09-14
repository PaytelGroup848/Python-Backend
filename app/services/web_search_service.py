import logging
import re
from typing import List, Dict

logger = logging.getLogger("web_search_service")


class WebSearchService:
    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Executes live web search using ddgs.
        Returns a list of dictionaries with title, url, and snippet.
        """
        results = []
        # Sanitize and extract clean search keywords
        clean_q = re.sub(
            r"\b(search\s+(the\s+)?web|search\s+online|search\s+internet|google\s+this|browse\s+the\s+web|please|find\s+out)\b",
            "",
            query,
            flags=re.IGNORECASE
        ).strip()
        # Take first line if multiline
        clean_q = clean_q.split("\n")[0].strip().strip("\"'*")
        if len(clean_q) > 120:
            clean_q = clean_q[:120].strip()
        if not clean_q:
            clean_q = query.strip()[:100]

        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(clean_q, max_results=max_results))
                for item in raw_results:
                    title = item.get("title") or "Web Result"
                    href = item.get("href") or ""
                    body = item.get("body") or ""
                    if href and (title or body):
                        results.append({
                            "title": title.strip(),
                            "url": href.strip(),
                            "snippet": body.strip(),
                        })
        except Exception as exc:
            logger.warning(f"Live web search error for '{clean_q}': {exc}")

        return results

    @staticmethod
    def format_search_context(results: List[Dict[str, str]]) -> str:
        """
        Formats search results into structured prompt context with numbered citations [1], [2]...
        """
        if not results:
            return ""

        lines = ["=== REAL-TIME LIVE WEB SEARCH RESULTS ==="]
        for i, res in enumerate(results, start=1):
            lines.append(f"[{i}] {res['title']}")
            lines.append(f"URL: {res['url']}")
            lines.append(f"Summary: {res['snippet']}\n")
        lines.append("=== END OF WEB SEARCH RESULTS ===")
        lines.append("INSTRUCTIONS: Use the real-time web search results above to answer the user question accurately. Cite your claims with inline numbers like [1], [2] corresponding to the sources above.")

        return "\n".join(lines)


web_search_service = WebSearchService()
