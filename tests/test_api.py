from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendation_endpoint_returns_ranked_items() -> None:
    response = client.get("/recommend/user_0001?k=5")

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "user_0001"
    assert len(body["results"]) == 5
