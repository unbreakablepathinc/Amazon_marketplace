"""
Oxylabs Web Scraper API client for Amazon Search (amazon.de).
Uses Realtime endpoint: POST https://realtime.oxylabs.io/v1/queries
"""
import logging
import httpx
from typing import Any

from app.config import settings

log = logging.getLogger(__name__)

OXYLABS_URL = "https://realtime.oxylabs.io/v1/queries"
AMAZON_DOMAIN = "de"


async def amazon_search(
    query: str,
    pages: int = 1,
    start_page: int = 1,
) -> dict[str, Any]:
    """
    Scrape Amazon search results via Oxylabs.
    Returns parsed JSON with results.organic, results.paid, etc.
    """
    payload = {
        "source": "amazon_search",
        "domain": AMAZON_DOMAIN,
        "query": query,
        "start_page": start_page,
        "pages": pages,
        "parse": True,
        "context": [{"key": "currency", "value": "EUR"}],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        log.info("Oxylabs request: query=%r pages=%s", query, pages)
        response = await client.post(
            OXYLABS_URL,
            auth=(settings.oxylabs_user, settings.oxylabs_password),
            json=payload,
        )
        if response.status_code >= 400:
            log.error("Oxylabs error %s: %s", response.status_code, response.text[:500])
        response.raise_for_status()
        data = response.json()
    # Oxylabs wraps result in results[0].content (content has .results.organic, .results.paid, etc.)
    if data.get("results"):
        content = data["results"][0].get("content") or {}
        return content
    return {}
