from __future__ import annotations

from app.reporting import build_report


def test_reranking_improves_diversity_without_collapsing_precision() -> None:
    report = build_report()

    assert report["users_evaluated"] == 18
    assert report["base_precision_at_5"] >= 0.78
    assert report["reranked_precision_at_5"] >= 0.72
    assert report["reranked_diversity_at_5"] > report["base_diversity_at_5"]
    assert report["reranked_novelty_at_5"] >= report["base_novelty_at_5"] - 0.05
