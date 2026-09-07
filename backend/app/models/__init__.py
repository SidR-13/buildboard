from app.models.failure_analysis import FailureAnalysis
from app.models.job import Job
from app.models.repo import Repo
from app.models.workflow_run import WorkflowRun

# Re-exported so callers import from `app.models`, and so importing this package registers
# every table on Base.metadata - which is what Alembic autogenerate reads.
__all__ = ["FailureAnalysis", "Job", "Repo", "WorkflowRun"]
