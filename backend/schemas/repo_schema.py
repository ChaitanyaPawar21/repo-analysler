"""
schemas/repo_schema.py - Repository Pydantic Schemas
=====================================================
Request and response schemas for repository-related endpoints.
Separates API contract from internal ORM models.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field


# =============================================================================
# Request Schemas
# =============================================================================

class RepoCreateRequest(BaseModel):
    """Schema for submitting a new repository for analysis."""
    github_url: HttpUrl = Field(
        ...,
        description="Full GitHub repository URL (e.g., https://github.com/owner/repo)",
        examples=["https://github.com/fastapi/fastapi"],
    )
    branch: Optional[str] = Field(
        default=None,
        description="Specific branch to analyze. Defaults to the repo's default branch.",
    )


# =============================================================================
# Response Schemas
# =============================================================================

class RepoResponse(BaseModel):
    """Schema for returning repository information."""
    id: uuid.UUID
    github_url: str
    owner: str
    name: str
    default_branch: str
    description: Optional[str] = None
    language: Optional[str] = None
    total_files: int = 0
    total_lines: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepoListResponse(BaseModel):
    """Paginated list of repositories."""
    total: int
    repositories: List[RepoResponse]


class AnalysisStatusResponse(BaseModel):
    """Schema for returning analysis status."""
    analysis_id: uuid.UUID
    repo_id: uuid.UUID
    status: str
    entry_points: Optional[List[str]] = None
    critical_files: Optional[List[dict]] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnalyzeResponse(BaseModel):
    """Response when an analysis is triggered."""
    message: str
    analysis_id: uuid.UUID
    repo_id: uuid.UUID
    status: str
