from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FailureAnalysis, WorkflowRun

router = APIRouter()


@router.get("/runs/{run_id}")
def get_run(run_id: UUID, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "repo_id": run.repo_id,
        "workflow_name": run.workflow_name,
        "branch": run.branch,
        "commit_sha": run.commit_sha,
        "status": run.status,
        "conclusion": run.conclusion,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "duration_seconds": run.duration_seconds,
    }


@router.get("/runs/{run_id}/analysis")
def get_run_analysis(run_id: UUID, db: Session = Depends(get_db)):
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    analysis = (
        db.query(FailureAnalysis).filter(FailureAnalysis.run_id == run_id).first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis for this run")

    return {
        "id": analysis.id,
        "run_id": analysis.run_id,
        "logs_snippet": analysis.logs_snippet,
        "claude_analysis": analysis.claude_analysis,
        "suggested_fix": analysis.suggested_fix,
        "created_at": analysis.created_at,
    }
