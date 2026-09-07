from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repo
from app.services.metrics_service import (
    calculate_average_duration,
    calculate_health_score,
    detect_flaky_builds,
)

router = APIRouter()


@router.get("/repos/{repo_id}/metrics")
def get_repo_metrics(repo_id: UUID, days: int = 30, db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    duration = calculate_average_duration(db, repo_id, days)
    health = calculate_health_score(db, repo_id, days)
    flaky = detect_flaky_builds(db, repo_id, days)

    return {**health, **duration, **flaky}
