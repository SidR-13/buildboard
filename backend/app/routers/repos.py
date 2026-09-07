from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repo, WorkflowRun

router = APIRouter()


@router.get("/repos")
def list_repos(db: Session = Depends(get_db)):
    repos = db.query(Repo).order_by(Repo.created_at.desc()).all()
    return [
        {
            "id": repo.id,
            "owner": repo.owner,
            "name": repo.name,
            "full_name": repo.full_name,
            "created_at": repo.created_at,
        }
        for repo in repos
    ]


@router.get("/repos/{repo_id}/runs")
def list_repo_runs(repo_id: UUID, limit: int = 50, db: Session = Depends(get_db)):
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")

    runs = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.repo_id == repo_id)
        .order_by(WorkflowRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": run.id,
            "workflow_name": run.workflow_name,
            "branch": run.branch,
            "commit_sha": run.commit_sha,
            "status": run.status,
            "conclusion": run.conclusion,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "duration_seconds": run.duration_seconds,
        }
        for run in runs
    ]
