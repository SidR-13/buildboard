from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import WorkflowRun


def calculate_pass_rate(db: Session, repo_id: UUID, days: int = 30) -> dict:
    since = datetime.utcnow() - timedelta(days=days)

    counts = (
        db.query(WorkflowRun.conclusion, func.count(WorkflowRun.id))
        .filter(
            WorkflowRun.repo_id == repo_id,
            WorkflowRun.conclusion.isnot(None),
            # Dropped from the denominator too, not just the numerator: a run that never
            # ran to completion wasn't tested, so counting it as a failure would be wrong.
            WorkflowRun.conclusion.notin_(["cancelled", "skipped"]),
            WorkflowRun.completed_at >= since,
        )
        .group_by(WorkflowRun.conclusion)
        .all()
    )

    total = sum(count for _, count in counts)
    successes = sum(count for conclusion, count in counts if conclusion == "success")

    # None rather than 0, so "no data yet" stays distinguishable from "everything failed"
    # all the way to the UI.
    if total == 0:
        return {"pass_rate": None, "total_runs": 0, "successful_runs": 0}

    return {
        "pass_rate": round((successes / total) * 100, 1),
        "total_runs": total,
        "successful_runs": successes,
    }


def _average_duration_between(db: Session, repo_id: UUID, start: datetime, end: datetime) -> float | None:
    # Successes only. Failure durations are bimodal - seconds for a syntax error, many minutes
    # for a flaky integration test - so mixing them in would not describe a typical build.
    return (
        db.query(func.avg(WorkflowRun.duration_seconds))
        .filter(
            WorkflowRun.repo_id == repo_id,
            WorkflowRun.conclusion == "success",
            WorkflowRun.completed_at >= start,
            WorkflowRun.completed_at < end,
        )
        .scalar()
    )


def calculate_average_duration(db: Session, repo_id: UUID, days: int = 30) -> dict:
    now = datetime.utcnow()
    avg_seconds = _average_duration_between(db, repo_id, now - timedelta(days=days), now)

    return {
        "avg_duration_seconds": round(avg_seconds, 1) if avg_seconds is not None else None,
    }


def calculate_health_score(db: Session, repo_id: UUID, days: int = 30) -> dict:
    pass_rate_data = calculate_pass_rate(db, repo_id, days)
    pass_rate = pass_rate_data["pass_rate"]

    if pass_rate is None:
        return {"health_score": None, **pass_rate_data}

    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = now - timedelta(days=days * 2)

    current_avg = _average_duration_between(db, repo_id, current_start, now)
    previous_avg = _average_duration_between(db, repo_id, previous_start, current_start)

    # The penalty is a trend (this window vs the one before it), not an absolute time threshold,
    # and caps at 20 points so pass rate stays dominant: a slowdown can make a green repo look
    # "healthy but slower", never broken.
    duration_penalty = 0.0
    if (
        current_avg is not None
        and previous_avg is not None
        and previous_avg > 0
        and current_avg > previous_avg
    ):
        pct_increase = ((current_avg - previous_avg) / previous_avg) * 100
        duration_penalty = min(20.0, pct_increase)

    health_score = round(max(0.0, pass_rate - duration_penalty), 1)

    return {"health_score": health_score, **pass_rate_data}


# A commit is flaky if the same (branch, sha) produced both a success and a failure.
# KNOWN LIMITATION: GitHub's "re-run failed jobs" reuses the same github_run_id, and the webhook
# handler updates that row in place, so the original failure is overwritten before this query ever
# sees both conclusions. Only genuinely separate runs over one commit are caught here.
def detect_flaky_builds(db: Session, repo_id: UUID, days: int = 30) -> dict:
    since = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(WorkflowRun.branch, WorkflowRun.commit_sha, WorkflowRun.conclusion)
        .filter(
            WorkflowRun.repo_id == repo_id,
            WorkflowRun.conclusion.in_(["success", "failure"]),
            WorkflowRun.completed_at >= since,
        )
        .all()
    )

    groups: dict[tuple[str, str], set[str]] = {}
    for branch, commit_sha, conclusion in rows:
        key = (branch, commit_sha)
        groups.setdefault(key, set()).add(conclusion)

    flaky_commits = [
        {"branch": branch, "commit_sha": commit_sha}
        for (branch, commit_sha), conclusions in groups.items()
        if {"success", "failure"}.issubset(conclusions)
    ]

    return {
        "flaky_count": len(flaky_commits),
        "flaky_commits": flaky_commits,
    }
