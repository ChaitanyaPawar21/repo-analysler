"""
utils/github_utils.py - GitHub Utility Functions
==================================================
Helper functions for interacting with the GitHub API and parsing URLs.
"""

import re
from typing import Tuple, Dict, Any, Optional

import httpx

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)

# Regex pattern to extract owner and repo name from GitHub URLs
GITHUB_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9\-_.]+)/([a-zA-Z0-9\-_.]+)/?(?:\.git)?$"
)


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Extract owner and repository name from a GitHub URL.

    Args:
        url: Full GitHub URL (e.g., https://github.com/owner/repo)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If the URL is not a valid GitHub repository URL.
    """
    # Strip trailing slashes and .git suffix
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    match = GITHUB_URL_PATTERN.match(url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")

    owner = match.group(1)
    repo_name = match.group(2)

    return owner, repo_name


async def fetch_repo_metadata(owner: str, repo_name: str) -> Dict[str, Any]:
    """
    Fetch repository metadata from the GitHub REST API.

    Args:
        owner: Repository owner (user or organization).
        repo_name: Repository name.

    Returns:
        Dict with keys: description, language, default_branch, stargazers_count, etc.
    """
    url = f"{settings.GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            return {
                "description": data.get("description"),
                "language": data.get("language"),
                "default_branch": data.get("default_branch", "main"),
                "stargazers_count": data.get("stargazers_count", 0),
                "forks_count": data.get("forks_count", 0),
                "open_issues_count": data.get("open_issues_count", 0),
                "size": data.get("size", 0),
                "topics": data.get("topics", []),
            }

    except httpx.HTTPStatusError as e:
        logger.error(
            "GitHub API error",
            status_code=e.response.status_code,
            owner=owner,
            repo=repo_name,
        )
        if e.response.status_code == 404:
            raise ValueError(f"Repository {owner}/{repo_name} not found on GitHub")
        raise
    except httpx.RequestError as e:
        logger.error("GitHub API request failed", error=str(e))
        # Return defaults if API is unreachable
        return {
            "description": None,
            "language": None,
            "default_branch": "main",
        }


async def clone_repository(
    owner: str,
    repo_name: str,
    target_dir: str,
    branch: Optional[str] = None,
) -> str:
    """
    Clone a GitHub repository to a local directory.

    Uses git CLI via subprocess for efficiency with large repos.

    Args:
        owner: Repository owner.
        repo_name: Repository name.
        target_dir: Base directory for clones.
        branch: Specific branch to clone (optional).

    Returns:
        Path to the cloned repository directory.
    """
    import asyncio
    from pathlib import Path

    clone_url = f"https://github.com/{owner}/{repo_name}.git"
    repo_dir = Path(target_dir) / f"{owner}__{repo_name}"

    if repo_dir.exists():
        logger.info("Repository already cloned", path=str(repo_dir))
        return str(repo_dir)

    repo_dir.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["git", "clone", "--depth", "1"]  # Shallow clone for speed
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([clone_url, str(repo_dir)])

    logger.info("Cloning repository", url=clone_url, target=str(repo_dir))

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        logger.error("Git clone failed", error=error_msg)
        raise RuntimeError(f"Failed to clone repository: {error_msg}")

    logger.info("Repository cloned successfully", path=str(repo_dir))
    return str(repo_dir)
