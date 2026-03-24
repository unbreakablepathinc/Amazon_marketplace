"""
API: Build thematic cluster for "dessertgläser" and compute product table
with KONZEPT proximity metrics.
"""
import logging
from collections import Counter

from fastapi import APIRouter, HTTPException

log = logging.getLogger(__name__)
from app.models.schemas import ClusterKeyword, ClusterResult, ProductRow, WordFromTitle
from app.services.oxylabs import amazon_search
from app.services.cluster import (
    extract_words_from_titles,
    extract_titles_from_search_result,
)
from app.services.analysis import aggregate_products
from app.services.llm_keywords import (
    extract_semantic_cluster_from_titles,
    count_keyword_in_titles,
)

MAIN_KEYWORD = "dessertgläser"
# Pages to scrape for building the cluster (titles only)
CLUSTER_BUILD_PAGES = 5
# Pages per cluster keyword for product/KONZEPT analysis (keep low for trial)
PAGES_PER_KEYWORD = 1


async def run_cluster_analysis() -> ClusterResult:
    """
    1) Scrape Amazon.de for MAIN_KEYWORD across several pages; collect product titles.
    2) Extract semantic keyword cluster (1–2 word terms) via Gemini prompt from those titles.
    3) For each cluster keyword, scrape 1 page and collect listings.
    4) Aggregate by ASIN: cluster_keywords_present, frequency, avg position, frequency_near_konzept.
    5) Return cluster keywords (with proportional weight) and product table.
    """
    # --- Collect product titles from main keyword pages ---
    all_titles_counter: dict[str, int] = {}
    product_titles: list[str] = []
    for page in range(1, CLUSTER_BUILD_PAGES + 1):
        content = await amazon_search(MAIN_KEYWORD, pages=1, start_page=page)
        search_result = {"results": content.get("results", content)}
        c = extract_words_from_titles(search_result)
        for w, count in c.items():
            all_titles_counter[w] = all_titles_counter.get(w, 0) + count
        product_titles.extend(extract_titles_from_search_result(search_result))

    # Full list of words from titles (frequency-based, for display)
    counter = Counter(all_titles_counter)
    all_words_from_titles = [
        WordFromTitle(keyword=w, occurrences=c) for w, c in counter.most_common()
    ]

    # --- LLM: extract semantic cluster from product titles (1–2 word keywords, up to 30) ---
    keyword_list = extract_semantic_cluster_from_titles(
        product_titles, seed=MAIN_KEYWORD, max_terms=30
    )
    if not keyword_list:
        raise HTTPException(
            status_code=503,
            detail="Cluster requires Gemini. Set GEMINI_API_KEY in .env and ensure product titles were collected.",
        )

    # Occurrences = how many titles contain each keyword; weight = proportional
    occurrences_list = [count_keyword_in_titles(kw, product_titles) for kw in keyword_list]
    total_occurrences = sum(occurrences_list) or 1
    cluster_keywords = [
        ClusterKeyword(
            keyword=kw,
            occurrences=occ,
            weight=round(occ / total_occurrences, 4) if total_occurrences else 0,
        )
        for kw, occ in zip(keyword_list, occurrences_list)
    ]

    # --- For each cluster keyword, fetch one page and collect results ---
    keyword_results: list[tuple[str, dict]] = []
    for kw in keyword_list:
        content = await amazon_search(kw, pages=PAGES_PER_KEYWORD, start_page=1)
        # content may be { "results": { "organic": [...], "paid": [...] } } or flat
        results = content.get("results", content)
        keyword_results.append((kw, {"results": results}))

    # --- Aggregate products and KONZEPT proximity ---
    product_dicts = aggregate_products(keyword_results)
    products = [ProductRow(**p) for p in product_dicts]

    return ClusterResult(
        main_keyword=MAIN_KEYWORD,
        cluster_keywords=cluster_keywords,
        all_words_from_titles=all_words_from_titles,
        product_titles=product_titles,
        products=products,
        total_keyword_occurrences=total_occurrences,
    )


router = APIRouter()


@router.post("/cluster/run", response_model=ClusterResult)
async def run_cluster():
    """Run full cluster analysis for dessertgläser and return cluster + product table."""
    try:
        log.info("Starting cluster analysis (dessertgläser)...")
        result = await run_cluster_analysis()
        log.info("Cluster analysis done: %s keywords, %s products", len(result.cluster_keywords), len(result.products))
        return result
    except Exception as e:
        log.exception("Cluster analysis failed: %s", e)
        raise
