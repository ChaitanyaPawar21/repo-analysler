"""
services/repo_service.py - Repository Service
===============================================
Handles repository CRUD operations and GitHub metadata fetching.
Acts as the bridge between API endpoints and the database layer.
"""

import uuid
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.repo import Repository
from schemas.repo_schema import RepoCreateRequest
from utils.github_utils import parse_github_url, fetch_repo_metadata
from core.logger import get_logger

logger = get_logger(__name__)


class RepoService:
    """
    Service for managing repository records.

    Responsibilities:
        - Create repository entries from GitHub URLs.
        - Fetch and update repository metadata from GitHub API.
        - List, retrieve, and soft-delete repositories.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_repository(self, request: RepoCreateRequest) -> Repository:
        """
        Create a new repository record after validating the GitHub URL.

        Args:
            request: Validated request with github_url and optional branch.

        Returns:
            The created Repository ORM instance.

        Raises:
            ValueError: If the repository already exists.
        """
        github_url = str(request.github_url)
        owner, name = parse_github_url(github_url)

        # Check for duplicates
        existing = await self.get_by_url(github_url)
        if existing:
            logger.info("Repository already exists", repo_id=str(existing.id))
            return existing

        # Fetch metadata from GitHub API
        metadata = await fetch_repo_metadata(owner, name)

        repo = Repository(
            github_url=github_url,
            owner=owner,
            name=name,
            default_branch=request.branch or metadata.get("default_branch", "main"),
            description=metadata.get("description"),
            language=metadata.get("language"),
        )

        self.db.add(repo)
        await self.db.flush()  # Get the ID without committing

        logger.info("Repository created", repo_id=str(repo.id), name=f"{owner}/{name}")
        return repo

    async def get_by_id(self, repo_id: uuid.UUID) -> Optional[Repository]:
        """Retrieve a repository by its UUID."""
        result = await self.db.execute(
            select(Repository).where(Repository.id == repo_id, Repository.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_url(self, github_url: str) -> Optional[Repository]:
        """Retrieve a repository by its GitHub URL."""
        result = await self.db.execute(
            select(Repository).where(Repository.github_url == github_url)
        )
        return result.scalar_one_or_none()

    async def list_repositories(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[List[Repository], int]:
        """
        List all active repositories with pagination.

        Returns:
            Tuple of (repositories list, total count).
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Repository.id)).where(Repository.is_active.is_(True))
        )
        total = count_result.scalar_one()

        # Get paginated results
        result = await self.db.execute(
            select(Repository)
            .where(Repository.is_active.is_(True))
            .order_by(Repository.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        repos = list(result.scalars().all())

        return repos, total

    async def delete_repository(self, repo_id: uuid.UUID) -> bool:
        """Soft-delete a repository by setting is_active to False."""
        repo = await self.get_by_id(repo_id)
        if not repo:
            return False
        repo.is_active = False
        await self.db.flush()
        logger.info("Repository soft-deleted", repo_id=str(repo_id))
        return True
