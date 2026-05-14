from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

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


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    report = build_report()
    preview_users = sorted(report["preview_recommendations"].keys() or ["user_0001"])
    sample_user = preview_users[0]
    strategy = report["selected_reranking_strategy"]
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recommendation Studio</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:860px;margin:48px auto;padding:0 24px;line-height:1.5;color:#111}}a{{color:#0645ad}}</style></head>
<body>
<h1>Recommendation Studio</h1>
<p>Recommendation workflow with candidate scoring, cold-start fallback, diversity-aware reranking, and serving APIs.</p>
<ul><li>Selected reranking strategy: {strategy}</li><li>Sample user: {sample_user}</li></ul>
<h2>Open endpoints</h2>
<ul>
<li><a href="/recommend/{sample_user}?k=5">Sample recommendation</a></li>
<li><a href="/users">Available users</a></li>
<li><a href="/health">Health check</a></li>
<li><a href="/docs">API docs</a></li>
</ul>
</body></html>"""


@app.get("/users")
def users() -> dict[str, list[str]]:
    report = build_report()
    return {"users": sorted(report["preview_recommendations"].keys() or ["user_0001"])}


@app.get("/recommend/{user_id}")
def recommend(user_id: str, k: int = TOP_K, preferred_category: str | None = None) -> dict[str, object]:
    report = build_report()
    preview = report["preview_recommendations"]
    if user_id in preview:
        return {
            "user_id": user_id,
            "strategy": "behavioral_rerank",
            "selected_reranking_strategy": report["selected_reranking_strategy"],
            "results": preview[user_id][:k],
        }

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
