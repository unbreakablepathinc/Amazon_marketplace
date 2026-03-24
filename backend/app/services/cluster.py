"""
Build thematic cluster: extract words from search result titles and take top 30 by frequency.
No product detail page crawling; only from titles in search results.
"""
import re
from collections import Counter
from typing import Any

# German stopwords and common non-thematic tokens to exclude from cluster
STOPWORDS = {
    "und", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "einem", "einen",
    "für", "mit", "von", "zu", "auf", "in", "im", "am", "an", "bei", "nach", "aus", "bis",
    "ist", "sind", "war", "werden", "wird", "haben", "hat", "kann", "können", "werden",
    "oder", "aber", "als", "auch", "noch", "nur", "schon", "sehr", "mehr", "zum", "zur",
    "pro", "x", "stück", "teil", "teile", "set", "pack", "paar", "mm", "cm", "ml", "l",
    "gr", "kg", "g", "st", "stk", "inkl", "versand", "prime", "amazon",
}
# Minimum length for a word to count
MIN_WORD_LEN = 3
# Max cluster size
CLUSTER_DEPTH = 30


def _normalize(word: str) -> str:
    w = word.lower().strip()
    w = re.sub(r"[^\wäöüß\-]", "", w)
    return w


def extract_titles_from_search_result(search_result: dict[str, Any]) -> list[str]:
    """Return list of all product titles from organic/paid/suggested/amazons_choices."""
    titles: list[str] = []
    results = search_result.get("results") or {}
    for list_type in ("organic", "paid", "suggested", "amazons_choices"):
        for item in results.get(list_type) or []:
            title = (item.get("title") or "").strip()
            if title:
                titles.append(title)
    return titles


def extract_words_from_titles(search_result: dict[str, Any]) -> Counter:
    """Extract all words from organic/paid/suggested/amazons_choices titles; return Counter."""
    counter: Counter = Counter()
    results = search_result.get("results") or {}
    for list_type in ("organic", "paid", "suggested", "amazons_choices"):
        for item in results.get(list_type) or []:
            title = (item.get("title") or "").strip()
            if not title:
                continue
            # Split on non-letters, keep words
            for raw in re.findall(r"[a-zA-ZäöüßÄÖÜ0-9\-]+", title):
                w = _normalize(raw)
                if len(w) >= MIN_WORD_LEN and w not in STOPWORDS:
                    counter[w] += 1
    return counter


def build_cluster_from_counter(counter: Counter, depth: int = CLUSTER_DEPTH) -> list[tuple[str, int]]:
    """Return top `depth` (keyword, count) sorted by count descending."""
    return counter.most_common(depth)
