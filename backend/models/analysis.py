"""
models/analysis.py - Analysis ORM Model
=========================================
SQLAlchemy model representing an analysis run on a repository.
Stores analysis status, results summary, and relationship to the repository.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base
from core.constants import AnalysisStatus


class Analysis(Base):
    """
    Represents a single analysis run against a repository.

    Each repository can have multiple analyses (e.g., re-analysis after updates).

    Attributes:
        id: Unique analysis identifier.
        repo_id: Foreign key to the analyzed repository.
        status: Current status of the analysis pipeline.
        entry_points: JSON list of detected entry point files.
        critical_files: JSON list of files identified as critical (high centrality).
        summary: AI-generated summary of the repository.
        graph_data: Serialized dependency graph metadata (node/edge counts, etc.).
        error_message: Error details if the analysis failed.
        started_at: When the analysis began.
        completed_at: When the analysis finished (success or failure).
    """

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    repo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50), default=AnalysisStatus.PENDING, nullable=False, index=True
    )
    entry_points: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    critical_files: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    graph_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship back to repository
    repository = relationship("Repository", back_populates="analyses", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, repo_id={self.repo_id}, status={self.status})>"
