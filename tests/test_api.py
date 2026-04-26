from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendation_endpoint_returns_ranked_items() -> None:
    response = client.get("/recommend/user_0001?k=5")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "user_0001"
    assert body["strategy"] == "behavioral_rerank"
    assert len(body["results"]) == 5


def test_unknown_user_uses_cold_start_content_fallback() -> None:
    response = client.get("/recommend/new_user_9000?k=4&preferred_category=wellness")

    assert response.status_code == 200
    body = response.json()
    assert body["strategy"] == "cold_start_content_fallback"
    assert body["preferred_category"] == "wellness"
    assert len(body["results"]) == 4
    assert body["results"][0]["category"] == "wellness"


def test_unknown_user_rejects_invalid_preferred_category() -> None:
    response = client.get("/recommend/new_user_9000?k=4&preferred_category=luxury")

    assert response.status_code == 400
