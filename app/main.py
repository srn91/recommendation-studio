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
<style>
body{{margin:0;background:#f8fafc;color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;line-height:1.5}}
main{{max-width:1080px;margin:0 auto;padding:56px 24px}}.hero{{background:linear-gradient(135deg,#111827,#be123c);color:white;border-radius:22px;padding:38px;box-shadow:0 24px 60px rgba(15,23,42,.18)}}
.eyebrow{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#fecdd3;font-weight:700}}h1{{font-size:42px;line-height:1.05;margin:10px 0 14px}}.hero p{{font-size:17px;color:#ffe4e6;max-width:780px}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:22px 0}}.card{{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:18px;box-shadow:0 10px 30px rgba(15,23,42,.06)}}
.metric{{font-size:25px;font-weight:800;color:#0f172a}}.label{{font-size:13px;color:#64748b;margin-top:3px}}.links{{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}}
a.button{{background:#0f172a;color:white;text-decoration:none;padding:11px 14px;border-radius:10px;font-weight:700}}a.secondary{{background:white;color:#0f172a;border:1px solid #cbd5e1}}
@media(max-width:800px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}h1{{font-size:34px}}}}
</style></head>
<body><main>
<section class="hero"><div class="eyebrow">Recommendation workflow</div><h1>Recommendation Studio</h1>
<p>Candidate scoring, cold-start fallback, diversity-aware reranking, and API serving for personalized recommendations.</p>
<div class="links"><a class="button" href="/recommend/{sample_user}?k=5">Sample recommendation</a><a class="button secondary" href="/users">Available users</a><a class="button secondary" href="/docs">API docs</a></div></section>
<section class="grid">
<div class="card"><div class="metric">{strategy}</div><div class="label">reranking strategy</div></div>
<div class="card"><div class="metric">{sample_user}</div><div class="label">sample user</div></div>
<div class="card"><div class="metric">18</div><div class="label">demo users</div></div>
<div class="card"><div class="metric">0.6</div><div class="label">diversity@5</div></div>
</section>
<section class="card"><p>The demo shows how a recommendation service can expose ranked results while preserving diversity, novelty, and fallback behavior for sparse users.</p></section>
</main></body></html>"""


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
