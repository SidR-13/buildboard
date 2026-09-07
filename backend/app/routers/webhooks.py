from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import verify_github_signature
from app.database import get_db
from app.models import FailureAnalysis, Repo, WorkflowRun
from app.services.claude_service import analyze_failure
from app.services.github_service import fetch_run_logs
from app.services.websocket_service import manager

router = APIRouter()


def _generate_failure_analysis(
    db: Session,
    run_id,
    owner: str,
    repo_name: str,
    github_run_id: int,
    workflow_name: str,
    branch: str,
    commit_sha: str,
) -> None:
    existing = db.query(FailureAnalysis).filter(FailureAnalysis.run_id == run_id).first()
    if existing is not None:
        return

    logs_snippet = fetch_run_logs(owner, repo_name, github_run_id)
    analysis = analyze_failure(workflow_name, branch, commit_sha, logs_snippet)

    failure = FailureAnalysis(
        run_id=run_id,
        logs_snippet=logs_snippet,
        claude_analysis=analysis["root_cause"],
        suggested_fix=analysis["suggested_fix"],
    )
    db.add(failure)
    db.commit()


def _parse_github_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _store_workflow_run(db: Session, payload: dict) -> tuple[Repo, WorkflowRun]:
    repo_data = payload["repository"]
    run_data = payload["workflow_run"]

    repo = db.query(Repo).filter(Repo.full_name == repo_data["full_name"]).first()
    if repo is None:
        repo = Repo(
            owner=repo_data["owner"]["login"],
            name=repo_data["name"],
            full_name=repo_data["full_name"],
            webhook_secret=settings.github_webhook_secret,
        )
        db.add(repo)
        db.flush()

    run = (
        db.query(WorkflowRun)
        .filter(WorkflowRun.github_run_id == run_data["id"])
        .first()
    )
    if run is None:
        run = WorkflowRun(repo_id=repo.id, github_run_id=run_data["id"])
        db.add(run)

    run.workflow_name = run_data["name"]
    run.branch = run_data["head_branch"]
    run.commit_sha = run_data["head_sha"]
    run.status = run_data["status"]
    run.conclusion = run_data["conclusion"]
    run.started_at = _parse_github_timestamp(run_data["run_started_at"])

    if run_data["status"] == "completed":
        run.completed_at = _parse_github_timestamp(run_data["updated_at"])
        if run.started_at and run.completed_at:
            run.duration_seconds = int((run.completed_at - run.started_at).total_seconds())

    db.commit()
    return repo, run


@router.post("/webhooks/github")
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()

    if not verify_github_signature(raw_body, x_hub_signature_256, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    if x_github_event == "workflow_run":
        repo, run = _store_workflow_run(db, payload)

        await manager.broadcast(
            repo.id,
            {
                "event": "run_update",
                "run": {
                    "id": str(run.id),
                    "github_run_id": run.github_run_id,
                    "workflow_name": run.workflow_name,
                    "branch": run.branch,
                    "commit_sha": run.commit_sha,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "duration_seconds": run.duration_seconds,
                },
            },
        )

        if run.status == "completed" and run.conclusion == "failure":
            background_tasks.add_task(
                _generate_failure_analysis,
                db,
                run.id,
                repo.owner,
                repo.name,
                run.github_run_id,
                run.workflow_name,
                run.branch,
                run.commit_sha,
            )

    return {"received": True, "event": x_github_event}
