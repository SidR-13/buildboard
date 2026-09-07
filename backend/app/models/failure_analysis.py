import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class FailureAnalysis(Base):
    __tablename__ = "failure_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False)
    logs_snippet = Column(Text, nullable=False)
    claude_analysis = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
