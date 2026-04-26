from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.config import TOP_K
from app.fallback import cold_start_recommendations, validate_preferred_category
from app.reporting import build_report


app = FastAPI(
    title="Recommendation Studio",
    description="A local-first recommendation workflow with diversity-aware reranking.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, object]:
    report = build_report()
    return {"status": "ok", "metrics": {k: v for k, v in report.items() if k != "preview_recommendations"}}


@app.get("/users")
def users() -> dict[str, list[str]]:
    report = build_report()
    return {"users": sorted(report["preview_recommendations"].keys() or ["user_0001"])}


@app.get("/recommend/{user_id}")
def recommend(user_id: str, k: int = TOP_K, preferred_category: str | None = None) -> dict[str, object]:
    report = build_report()
    preview = report["preview_recommendations"]
    if user_id in preview:
        return {"user_id": user_id, "strategy": "behavioral_rerank", "results": preview[user_id][:k]}

    try:
        validate_preferred_category(preferred_category)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"unknown preferred_category: {preferred_category}") from exc

    return {
        "user_id": user_id,
        "strategy": "cold_start_content_fallback",
        "preferred_category": preferred_category,
        "results": cold_start_recommendations(k=k, preferred_category=preferred_category),
    }
