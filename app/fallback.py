from __future__ import annotations

from app.dataset import build_catalog
from app.reranking import rerank_for_diversity


def _known_categories() -> set[str]:
    return {item.category for item in build_catalog()}


def validate_preferred_category(preferred_category: str | None) -> None:
    if preferred_category is None:
        return
    if preferred_category not in _known_categories():
        raise ValueError(preferred_category)


def cold_start_recommendations(k: int, preferred_category: str | None = None) -> list[dict[str, object]]:
    validate_preferred_category(preferred_category)
    rows: list[dict[str, object]] = []
    for item in build_catalog():
        category_match = 1.0 if preferred_category == item.category else 0.0
        base_score = (
            0.46 * category_match
            + 0.34 * item.popularity
            + 0.20 * item.novelty
        )
        rows.append(
            {
                "item_id": item.item_id,
                "category": item.category,
                "category_match": round(category_match, 6),
                "popularity": item.popularity,
                "novelty": item.novelty,
                "exploration_bias": 0.22,
                "price_sensitivity": 0.35,
                "base_score": round(base_score, 6),
                "fallback_reason": "content_metadata_prior",
            }
        )
    return rerank_for_diversity(rows, k)
