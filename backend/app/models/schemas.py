from pydantic import BaseModel
from typing import Optional


class ClusterKeyword(BaseModel):
    keyword: str
    occurrences: int
    weight: float  # proportional share (e.g. 20/35 for 20 occurrences out of 35 total)


class ProductRow(BaseModel):
    asin: str
    image: Optional[str] = None
    price: Optional[float] = None
    cluster_keywords_present: int
    frequency_in_cluster_results: int
    average_position: float
    frequency_near_konzept: int


class WordFromTitle(BaseModel):
    keyword: str
    occurrences: int


class ClusterResult(BaseModel):
    main_keyword: str
    cluster_keywords: list[ClusterKeyword]
    all_words_from_titles: list[WordFromTitle]  # full cluster of words from titles (sorted by count)
    product_titles: list[str]  # raw product titles from dessertgläser search pages
    products: list[ProductRow]
    total_keyword_occurrences: int
