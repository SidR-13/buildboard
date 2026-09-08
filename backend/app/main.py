from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import metrics, repos, runs, webhooks, ws

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# /api, not root: the frontend's client-side routes (e.g. /runs/:runId) and this API's
# resource paths (e.g. GET /runs/{id}) are otherwise identical shapes once both are served
# from the same domain - Nginx can't tell "give me the page" from "give me the JSON" for
# the same URL. /health stays unprefixed (see main.py below) since nothing in the frontend
# ever routes to /health, so it can't collide.
app.include_router(webhooks.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(repos.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(ws.router, prefix="/api")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
