from __future__ import annotations

from dataclasses import dataclass

from app.config import CATALOG_SIZE, USER_COUNT


@dataclass(frozen=True)
class CatalogItem:
    item_id: str
    category: str
    popularity: float
    novelty: float


@dataclass(frozen=True)
class UserProfile:
    user_id: str
    preferred_category: str
    exploration_bias: float
    price_sensitivity: float


def build_catalog() -> list[CatalogItem]:
    categories = ["outdoor", "wellness", "productivity", "gaming"]
    items: list[CatalogItem] = []
    for index in range(CATALOG_SIZE):
        category = categories[index % len(categories)]
        popularity = round(0.9 - index * 0.02, 6)
        novelty = round(1.0 - popularity, 6)
        items.append(
            CatalogItem(
                item_id=f"item_{index + 1:04d}",
                category=category,
                popularity=max(0.05, popularity),
                novelty=max(0.05, novelty),
            )
        )
    return items


def build_users() -> list[UserProfile]:
    categories = ["outdoor", "wellness", "productivity", "gaming"]
    users: list[UserProfile] = []
    for index in range(USER_COUNT):
        users.append(
            UserProfile(
                user_id=f"user_{index + 1:04d}",
                preferred_category=categories[index % len(categories)],
                exploration_bias=round(0.15 + (index % 3) * 0.08, 6),
                price_sensitivity=round(0.25 + (index % 4) * 0.12, 6),
            )
        )
    return users


def build_interactions() -> list[dict[str, object]]:
    catalog = build_catalog()
    users = build_users()
    rows: list[dict[str, object]] = []
    secondary_category_map = {
        "outdoor": "wellness",
        "wellness": "productivity",
        "productivity": "gaming",
        "gaming": "outdoor",
    }
    for user in users:
        for item in catalog:
            if item.category == user.preferred_category:
                category_match = 1.0
            elif item.category == secondary_category_map[user.preferred_category]:
                category_match = 0.55
            else:
                category_match = 0.0
            relevance_signal = (
                0.44 * category_match
                + 0.18 * item.popularity
                + 0.24 * user.exploration_bias * item.novelty
                + 0.18 * (1.0 - min(category_match, 1.0)) * user.exploration_bias
            )
            clicked = 1 if relevance_signal >= 0.34 else 0
            rows.append(
                {
                    "user_id": user.user_id,
                    "item_id": item.item_id,
                    "category": item.category,
                    "category_match": category_match,
                    "popularity": item.popularity,
                    "novelty": item.novelty,
                    "exploration_bias": user.exploration_bias,
                    "price_sensitivity": user.price_sensitivity,
                    "clicked": clicked,
                }
            )
    return rows
