from __future__ import annotations

from sklearn.ensemble import GradientBoostingClassifier

from app.dataset import build_interactions


def train_model(seed: int = 20260426) -> tuple[GradientBoostingClassifier, list[dict[str, object]]]:
    rows = build_interactions()
    model = GradientBoostingClassifier(random_state=seed)
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
    labels = [row["clicked"] for row in rows]
    model.fit(features, labels)
    return model, rows
