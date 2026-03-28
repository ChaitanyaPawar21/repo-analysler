"""
api/v1/endpoints/critical_files.py - Critical Files Endpoints
==============================================================
Endpoints for retrieving files identified as critical based on
dependency graph centrality metrics.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db_session
from services.analysis_service import AnalysisService
from core.constants import AnalysisStatus
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/{repo_id}",
    summary="Get critical files",
    description="Retrieve files identified as critical based on dependency analysis.",
)
async def get_critical_files(
    repo_id: uuid.UUID,
    top_n: int = Query(10, ge=1, le=50, description="Number of top critical files to return"),
    req: Request = None,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Return the most critical files in a repository.

    Critical files are determined by graph centrality metrics:
        - **Betweenness centrality**: Files that bridge many dependency paths.
        - **In-degree**: Files imported by many other files.
        - **PageRank**: Files with high influence in the dependency network.

    These files represent potential single points of failure and should
    receive extra attention during code reviews and testing.

    Prerequisites:
        - Analysis must be completed for this repository.
    """
    vector_store = req.app.state.vector_store
    service = AnalysisService(db=db, vector_store=vector_store)
    analysis = await service.get_latest_analysis(repo_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis found for repository {repo_id}",
        )

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Analysis is not completed. Current status: {analysis.status}",
        )

    critical_files = analysis.critical_files or []

    # Apply top_n limit (data may already be limited, but enforce client-side limit)
    critical_files = critical_files[:top_n]

    return {
        "repo_id": str(repo_id),
        "analysis_id": str(analysis.id),
        "total_critical_files": len(critical_files),
        "critical_files": critical_files,
    }
