from __future__ import annotations

import json
from pathlib import Path

from app.config import GENERATED_DIR, TOP_K
from app.evaluation import diversity_at_k, novelty_at_k, precision_at_k
from app.fallback import cold_start_recommendations
from app.reranking import rerank_for_diversity
from app.training import train_model


def _portable(path: Path) -> str:
    cwd = Path.cwd()
    try:
        return str(path.relative_to(cwd))
    except ValueError:
        return str(path)


def build_report(seed: int = 20260426) -> dict[str, object]:
    model, rows = train_model(seed=seed)
    features = [
        [
            row["category_match"],
            row["popularity"],
            row["novelty"],
            row["exploration_bias"],
            row["price_sensitivity"],
        ]
        for row in rows
    ]
    probabilities = model.predict_proba(features)[:, 1]
    scored_rows: list[dict[str, object]] = []
    for row, probability in zip(rows, probabilities, strict=True):
        enriched = dict(row)
        enriched["base_score"] = round(float(probability), 6)
        scored_rows.append(enriched)

    reranked_rows: list[dict[str, object]] = []
    user_ids = sorted({str(row["user_id"]) for row in scored_rows})
    preview: dict[str, list[dict[str, object]]] = {}
    for user_id in user_ids:
        user_rows = [row for row in scored_rows if row["user_id"] == user_id]
        reranked = rerank_for_diversity(user_rows, TOP_K)
        reranked_rows.extend(reranked)
        if user_id == "user_0001":
            preview[user_id] = reranked

    report = {
        "users_evaluated": len(user_ids),
        "base_precision_at_5": round(precision_at_k(scored_rows, "base_score", TOP_K), 4),
        "base_novelty_at_5": round(novelty_at_k(scored_rows, "base_score", TOP_K), 4),
        "base_diversity_at_5": round(diversity_at_k(scored_rows, "base_score", TOP_K), 4),
        "reranked_precision_at_5": round(precision_at_k(reranked_rows, "rerank_score", TOP_K), 4),
        "reranked_novelty_at_5": round(novelty_at_k(reranked_rows, "rerank_score", TOP_K), 4),
        "reranked_diversity_at_5": round(diversity_at_k(reranked_rows, "rerank_score", TOP_K), 4),
        "preview_recommendations": preview,
        "cold_start_preview": {
            "preferred_category": "wellness",
            "results": cold_start_recommendations(TOP_K, preferred_category="wellness"),
        },
    }
    return report


def render_markdown(report: dict[str, object]) -> str:
    preview_rows = report["preview_recommendations"]["user_0001"]
    lines = [
        "# Recommendation Summary",
        "",
        f"Users evaluated: `{report['users_evaluated']}`",
        "",
        "## Metrics",
        "",
        f"- base precision@5: `{report['base_precision_at_5']}`",
        f"- base novelty@5: `{report['base_novelty_at_5']}`",
        f"- base diversity@5: `{report['base_diversity_at_5']}`",
        f"- reranked precision@5: `{report['reranked_precision_at_5']}`",
        f"- reranked novelty@5: `{report['reranked_novelty_at_5']}`",
        f"- reranked diversity@5: `{report['reranked_diversity_at_5']}`",
        "",
        "## Sample Reranked List (user_0001)",
        "",
    ]
    for row in preview_rows:
        lines.append(
            f"- `{row['item_id']}` category=`{row['category']}` base_score=`{row['base_score']}` rerank_score=`{row['rerank_score']}`"
        )
    lines.extend(
        [
            "",
            "## Cold-Start Fallback Preview",
            "",
            "Preferred category: `wellness`",
            "",
        ]
    )
    for row in report["cold_start_preview"]["results"]:
        lines.append(
            f"- `{row['item_id']}` category=`{row['category']}` base_score=`{row['base_score']}` rerank_score=`{row['rerank_score']}`"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict[str, object]) -> tuple[str, str]:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    json_path = GENERATED_DIR / "recommendation_report.json"
    markdown_path = GENERATED_DIR / "recommendation_summary.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return _portable(json_path), _portable(markdown_path)
