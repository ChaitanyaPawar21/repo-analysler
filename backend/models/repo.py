"""
models/repo.py - Repository ORM Model
=======================================
SQLAlchemy model representing a GitHub repository tracked in the system.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base


class Repository(Base):
    """
    Represents a GitHub repository that has been submitted for analysis.

    Attributes:
        id: Unique identifier (UUID).
        github_url: Full GitHub URL of the repository.
        owner: Repository owner (user or organization).
        name: Repository name.
        default_branch: Default branch (e.g., main, master).
        description: Repository description from GitHub.
        language: Primary language detected.
        total_files: Count of files in the repository.
        total_lines: Total lines of code.
        clone_path: Local filesystem path where the repo was cloned.
        is_active: Soft-delete flag.
        created_at: When the repo was first added.
        updated_at: Last modification timestamp.
    """

    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    github_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    clone_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to analyses
    analyses = relationship("Analysis", back_populates="repository", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, name={self.owner}/{self.name})>"
