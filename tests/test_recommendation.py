from __future__ import annotations

from app.fallback import cold_start_recommendations
from app.reporting import build_report


def test_reranking_improves_diversity_without_collapsing_precision() -> None:
    report = build_report()

    assert report["users_evaluated"] == 18
    assert report["base_precision_at_5"] >= 0.78
    assert report["reranked_precision_at_5"] >= 0.72
    assert report["reranked_diversity_at_5"] > report["base_diversity_at_5"]
    assert report["reranked_novelty_at_5"] >= report["base_novelty_at_5"] - 0.05
    assert report["selected_reranking_strategy"] in {"diversity_rerank", "novelty_blend_rerank"}
    assert set(report["strategy_comparison"]) == {"diversity_rerank", "novelty_blend_rerank"}


def test_cold_start_fallback_uses_category_metadata_when_present() -> None:
    results = cold_start_recommendations(k=5, preferred_category="wellness")

    assert len(results) == 5
    assert results[0]["category"] == "wellness"
    assert all(row["fallback_reason"] == "content_metadata_prior" for row in results)
