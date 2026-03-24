"""
Semantic keyword cluster extraction using Gemini (prompt-based).
"""
import logging
import re
from typing import Optional

from app.config import settings

log = logging.getLogger(__name__)

# Prompt: extract semantic keyword cluster FROM product titles (1–2 words, normalize, semantic selection)
EXTRACT_CLUSTER_FROM_TITLES_TEMPLATE = '''From the product titles below, extract a semantic keyword cluster for the seed term: SEED = "{seed}"

LANGUAGE: Include keywords in ALL languages that appear in the titles (German, English, French, Italian, Spanish, and any other language). Do not restrict to one language; keep the exact wording as in the titles.

CRITICAL OUTPUT REQUIREMENTS:
- Extract ONLY keywords that are 1 OR 2 words long (exactly one or two tokens separated by a space).
- Two-word keywords are REQUIRED in the output when they exist in the titles (do not collapse them into a single word).
- Do NOT write explanations. Output only the final keyword list.

HOW TO EXTRACT CANDIDATES (mandatory):
1) First, scan all titles and extract every meaningful 1–2 word noun phrase that appears in the titles (examples: "joghurtgläser", "eisbecher", "dessertschalen", "dessert glasses", "ice cream cups", "nachtisch gläser", "weck gläser", "tulpenform").
2) Normalize:
   - lowercase
   - fix obvious casing/umlauts if needed
   - keep singular/plural as seen (you may include both if both appear)
3) Remove exact duplicates only.

SEMANTIC SELECTION (mandatory):
4) From the extracted candidate list, keep the terms that are semantically closest to the seed "{seed}" (same product family or direct substitute on Amazon DE).
5) Do NOT over-filter: if a term is plausibly used by shoppers to find dessert glasses, keep it.
6) Return up to 30 terms; if fewer exist, return fewer.

OUTPUT FORMAT: One keyword per line, no numbering, no commas, no quotes.

TITLES:
{titles}
'''


# Prompt: select 30 meaningful keywords FROM the frequency-extracted candidates (from cluster.py)
SELECT_CLUSTER_FROM_CANDIDATES_TEMPLATE = '''You are an Amazon DE keyword clustering expert. From the CANDIDATE list below, select EXACTLY 30 keywords that are meaningful as PRODUCT TYPES or DESSERT/FOOD NAMES for the seed: SEED = "{seed}" (dessert glasses).

LANGUAGE: Include keywords in ALL languages (German, English, French, Italian, Spanish, etc.). Use the exact spelling as in the CANDIDATES list; do not restrict to one language.

INCLUDE only:
- Product type names: same category as "{seed}" or direct substitute (e.g. dessertschalen, dessertbecher, eisbecher, joghurtgläser, eisschalen, mousse, tiramisu, pudding, nachtisch, desserts).
- Dessert/food names or serving contexts that describe WHAT is served in such glasses (e.g. eiscreme, joghurt, marmelade).

EXCLUDE strictly (do not select these even if they have high count):
- Materials: plastik, glas, glass, etc.
- Attributes: wiederverwendbar, spülmaschinenfest, kleine, mini, etc.
- Quantities/pack sizes: 6er, 12er, 200, 160ml, 200ml, or any number-only or "Xer" (set of X).
- Accessories/parts: deckel, löffeln, etc.
- Generic usage words: party, etc.

RULES:
- Use ONLY keywords that appear in the CANDIDATES list below. Exact same spelling. Do not add new words.
- Output exactly 30 keywords, one per line, no numbering, no commas, no quotes, no explanation.
- Order: most relevant product types first, then by relevance; prefer higher frequency when relevance is equal.

CANDIDATES (keyword, count):
{candidates}
'''


def extract_semantic_cluster_from_titles(
    titles: list[str],
    seed: str = "dessertgläser",
    max_terms: int = 30,
) -> Optional[list[str]]:
    """
    Extract semantic keyword cluster (1–2 word terms) from product titles via LLM.
    Uses EXTRACT_CLUSTER_FROM_TITLES_TEMPLATE: extract candidates, normalize, then select up to max_terms closest to seed.
    Returns up to max_terms keywords, or None if Gemini is not configured or fails.
    """
    if not titles:
        log.warning("extract_semantic_cluster_from_titles: no titles provided")
        return None
    if not settings.gemini_api_key:
        log.warning("extract_semantic_cluster_from_titles: GEMINI_API_KEY is not set")
        return None
    titles_text = "\n".join(t.strip() for t in titles if t and t.strip())
    if not titles_text:
        log.warning("extract_semantic_cluster_from_titles: titles are empty after strip")
        return None
    prompt = EXTRACT_CLUSTER_FROM_TITLES_TEMPLATE.format(seed=seed, titles=titles_text)
    return _call_gemini_and_parse_keywords(prompt, max_terms=max_terms)


def select_semantic_cluster_from_candidates(
    candidates: list[tuple[str, int]],
    seed: str = "dessertgläser",
    max_terms: int = 30,
) -> Optional[list[str]]:
    """
    Use LLM to select the top max_terms meaningful keywords from frequency-extracted candidates (from cluster.py).
    Returns up to max_terms keywords, or None if Gemini is not configured or fails.
    """
    if not candidates:
        log.warning("select_semantic_cluster_from_candidates: no candidates provided")
        return None
    if not settings.gemini_api_key:
        log.warning("select_semantic_cluster_from_candidates: GEMINI_API_KEY is not set")
        return None
    # Format: one per line "keyword (count)"
    candidates_text = "\n".join("%s (%d)" % (kw, cnt) for kw, cnt in candidates)
    prompt = SELECT_CLUSTER_FROM_CANDIDATES_TEMPLATE.format(seed=seed, candidates=candidates_text)
    return _call_gemini_and_parse_keywords(prompt, max_terms=max_terms)


def _call_gemini_and_parse_keywords(prompt: str, max_terms: int = 30) -> Optional[list[str]]:
    """Call Gemini with prompt; parse response to list of keywords (one per line); return up to max_terms."""
    if not settings.gemini_api_key:
        return None
    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        MODELS_TO_TRY = (
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-3-flash-preview",
        )
        response = None
        last_err = None
        for model in MODELS_TO_TRY:
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                log.info("Gemini succeeded with model %s", model)
                break
            except Exception as model_err:
                last_err = model_err
                err_str = str(model_err)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    log.warning("Gemini %s: quota exceeded (429), trying next", model)
                    continue
                if "404" in err_str or "NOT_FOUND" in err_str:
                    log.warning("Gemini %s: model not found (404), trying next", model)
                    continue
                if "400" in err_str or "FAILED_PRECONDITION" in err_str or "location is not supported" in err_str.lower():
                    log.warning("Gemini %s: location not supported (400), trying next", model)
                    continue
                raise
        if response is None:
            raise RuntimeError(
                "Gemini failed for all models. Check quota/location/API key. Last error: %s" % (last_err,)
            )
        text = getattr(response, "text", None) or ""
        keywords = []
        for line in text.splitlines():
            line = line.strip()
            line = re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
            line = line.strip('"\'')
            if line and len(line) <= 80:
                keywords.append(line)
        if not keywords:
            log.warning("Gemini returned no parseable keywords. Raw length=%s", len(text))
        return keywords[:max_terms] if keywords else None
    except Exception as e:
        log.exception("Gemini API failed: %s", e)
        return None


def count_keyword_in_titles(keyword: str, titles: list[str]) -> int:
    """Count how many titles contain the keyword (case-insensitive, as phrase)."""
    k = keyword.lower()
    return sum(1 for t in titles if k in t.lower())
