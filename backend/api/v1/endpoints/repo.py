"""
api/v1/endpoints/repo.py - Repository Endpoints
=================================================
CRUD endpoints for managing GitHub repositories.
Handles repository registration, listing, retrieval, and deletion.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db_session
from services.repo_service import RepoService
from schemas.repo_schema import (
    RepoCreateRequest,
    RepoResponse,
    RepoListResponse,
)

router = APIRouter()


@router.post(
    "/",
    response_model=RepoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new repository",
    description="Submit a GitHub repository URL to track and prepare for analysis.",
)
async def create_repository(
    request: RepoCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Register a new GitHub repository for analysis.

    - Validates the GitHub URL format.
    - Fetches repository metadata from the GitHub API.
    - Creates a database record for tracking.
    - Returns the created repository with metadata.
    """
    service = RepoService(db)
    repo = await service.create_repository(request)
    return repo


@router.get(
    "/",
    response_model=RepoListResponse,
    summary="List all repositories",
    description="Retrieve a paginated list of all tracked repositories.",
)
async def list_repositories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """List all active repositories with pagination."""
    service = RepoService(db)
    repos, total = await service.list_repositories(skip=skip, limit=limit)
    return RepoListResponse(total=total, repositories=repos)


@router.get(
    "/{repo_id}",
    response_model=RepoResponse,
    summary="Get repository details",
    description="Retrieve detailed information about a specific repository.",
)
async def get_repository(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single repository by its UUID."""
    service = RepoService(db)
    repo = await service.get_by_id(repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {repo_id} not found",
        )
    return repo


@router.delete(
    "/{repo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a repository",
    description="Soft-delete a repository (marks inactive, preserves data).",
)
async def delete_repository(
    repo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Soft-delete a repository by UUID."""
    service = RepoService(db)
    deleted = await service.delete_repository(repo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {repo_id} not found",
        )
