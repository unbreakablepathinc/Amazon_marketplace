"""
Aggregate products across cluster keyword results and compute:
- Number of cluster keywords in which the product appears
- Frequency of appearance in cluster results
- Average position
- Frequency of appearance on a page where a KONZEPT product also appears
"""
from collections import defaultdict
from typing import Any

BRAND_KONZEPT = "KONZEPT"


def _collect_listings(search_result: dict[str, Any], keyword: str) -> tuple[list[dict], set[str]]:
    """
    Collect all listings (organic, paid, etc.) with keyword and position.
    Also return set of ASINs that are KONZEPT brand on this page.
    """
    rows: list[dict] = []
    konzept_asins: set[str] = set()
    results = search_result.get("results") or {}
    pos = 0
    for list_type in ("organic", "paid", "suggested", "amazons_choices"):
        for item in results.get(list_type) or []:
            pos += 1
            asin = (item.get("asin") or "").strip()
            if not asin:
                continue
            manufacturer = (item.get("manufacturer") or "").strip().upper()
            if BRAND_KONZEPT in manufacturer.upper():
                konzept_asins.add(asin)
            rows.append({
                "asin": asin,
                "title": item.get("title"),
                "price": item.get("price"),
                "url_image": item.get("url_image"),
                "keyword": keyword,
                "position": pos,
            })
    return rows, konzept_asins


def aggregate_products(
    keyword_results: list[tuple[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """
    keyword_results: list of (keyword, search_result) for each cluster keyword.
    Returns list of product dicts with ASIN, image, price, cluster_keywords_present,
    frequency_in_cluster_results, average_position, frequency_near_konzept.
    """
    # asin -> { keywords_seen, total_appearances, position_sum, near_konzept_count, best price, best image }
    by_asin: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "keywords_seen": set(),
            "total_appearances": 0,
            "position_sum": 0,
            "near_konzept_count": 0,
            "price": None,
            "url_image": None,
        }
    )
    for keyword, search_result in keyword_results:
        rows, konzept_asins = _collect_listings(search_result, keyword)
        page_has_konzept = len(konzept_asins) > 0
        for r in rows:
            asin = r["asin"]
            rec = by_asin[asin]
            rec["keywords_seen"].add(keyword)
            rec["total_appearances"] += 1
            rec["position_sum"] += r["position"]
            if page_has_konzept:
                rec["near_konzept_count"] += 1
            if rec["price"] is None and r.get("price") is not None:
                rec["price"] = r["price"]
            if rec["url_image"] is None and r.get("url_image"):
                rec["url_image"] = r["url_image"]
    out = []
    for asin, rec in by_asin.items():
        n_kw = len(rec["keywords_seen"])
        total = rec["total_appearances"]
        pos_sum = rec["position_sum"]
        avg_pos = pos_sum / total if total else 0
        out.append({
            "asin": asin,
            "image": rec["url_image"],
            "price": rec["price"],
            "cluster_keywords_present": n_kw,
            "frequency_in_cluster_results": total,
            "average_position": round(avg_pos, 2),
            "frequency_near_konzept": rec["near_konzept_count"],
        })
    return sorted(out, key=lambda x: (-x["frequency_in_cluster_results"], x["average_position"]))
