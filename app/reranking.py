from __future__ import annotations


def rerank_for_diversity(rows: list[dict[str, object]], k: int) -> list[dict[str, object]]:
    remaining = sorted(rows, key=lambda row: row["base_score"], reverse=True)
    selected: list[dict[str, object]] = []
    category_counts: dict[str, int] = {}

    target_distinct = min(3, k, len({str(row["category"]) for row in remaining}))
    seen_categories: set[str] = set()
    distinct_category_candidates = sorted(
        remaining,
        key=lambda row: (row["base_score"] + 0.18 * row["novelty"]),
        reverse=True,
    )
    for row in distinct_category_candidates:
        category = str(row["category"])
        if category in seen_categories:
            continue
        chosen = row.copy()
        chosen["rerank_score"] = round(row["base_score"] + 0.18 * row["novelty"] + 0.12, 6)
        selected.append(chosen)
        seen_categories.add(category)
        category_counts[category] = 1
        remaining.remove(row)
        if len(selected) >= target_distinct:
            break

    while remaining and len(selected) < k:
        best_index = 0
        best_score = float("-inf")
        for index, row in enumerate(remaining):
            seen_count = category_counts.get(str(row["category"]), 0)
            diversity_bonus = 0.10 if seen_count == 0 else 0.0
            repeat_penalty = 0.08 * seen_count
            rerank_score = row["base_score"] + diversity_bonus - repeat_penalty + 0.04 * row["novelty"]
            if rerank_score > best_score:
                best_index = index
                best_score = rerank_score
        chosen = remaining.pop(best_index).copy()
        chosen["rerank_score"] = round(best_score, 6)
        selected.append(chosen)
        category = str(chosen["category"])
        category_counts[category] = category_counts.get(category, 0) + 1

    return selected
