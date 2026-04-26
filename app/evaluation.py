from __future__ import annotations

from collections import defaultdict


def precision_at_k(rows: list[dict[str, object]], score_key: str, k: int = 5) -> float:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["user_id"])].append(row)

    precisions: list[float] = []
    for user_rows in grouped.values():
        ranked = sorted(user_rows, key=lambda row: row[score_key], reverse=True)[:k]
        precisions.append(sum(int(row["clicked"]) for row in ranked) / k)
    return sum(precisions) / len(precisions)


def novelty_at_k(rows: list[dict[str, object]], score_key: str, k: int = 5) -> float:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["user_id"])].append(row)
    scores: list[float] = []
    for user_rows in grouped.values():
        ranked = sorted(user_rows, key=lambda row: row[score_key], reverse=True)[:k]
        scores.append(sum(float(row["novelty"]) for row in ranked) / k)
    return sum(scores) / len(scores)


def diversity_at_k(rows: list[dict[str, object]], score_key: str, k: int = 5) -> float:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["user_id"])].append(row)
    scores: list[float] = []
    for user_rows in grouped.values():
        ranked = sorted(user_rows, key=lambda row: row[score_key], reverse=True)[:k]
        distinct_categories = len({str(row["category"]) for row in ranked})
        scores.append(distinct_categories / k)
    return sum(scores) / len(scores)
