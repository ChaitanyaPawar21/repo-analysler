"""
api/v1/endpoints/analyze.py - Analysis Endpoints
==================================================
Triggers repository analysis and retrieves analysis status/results.
Uses FastAPI BackgroundTasks for async processing.

Migration Note:
    To switch to Celery, replace `background_tasks.add_task(...)` with
    `analysis_task.delay(analysis.id)` — the service layer stays unchanged.
"""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db_session
from services.repo_service import RepoService
from services.analysis_service import AnalysisService
from schemas.repo_schema import AnalyzeResponse, AnalysisStatusResponse, RepoCreateRequest
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


async def _run_analysis_background(analysis_id: uuid.UUID, db: AsyncSession, vector_store):
    """
    Wrapper function for running analysis as a BackgroundTask.

    This isolates the background work and handles its own DB session lifecycle.
    When migrating to Celery, this becomes the task function body.
    """
    service = AnalysisService(db=db, vector_store=vector_store)
    await service.run_analysis(analysis_id)


@router.post(
    "/",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger repository analysis",
    description="Submit a GitHub repo URL for full analysis. Processing runs in the background.",
)
async def trigger_analysis(
    request: RepoCreateRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Trigger a full analysis pipeline for a repository.

    Steps:
        1. Create or retrieve the repository record.
        2. Create a new Analysis entry in PENDING status.
        3. Dispatch background task to run the analysis pipeline.
        4. Return immediately with the analysis ID for polling.

    The client can poll GET /analyze/{analysis_id} for status updates.
    """
    # Step 1: Ensure repository exists
    repo_service = RepoService(db)
    repo = await repo_service.create_repository(request)

    # Step 2: Create analysis record
    vector_store = req.app.state.vector_store
    analysis_service = AnalysisService(db=db, vector_store=vector_store)
    analysis = await analysis_service.create_analysis(repo.id)
    await db.commit()

    # Step 3: Dispatch background analysis
    # NOTE: When migrating to Celery, replace the line below with:
    #   analysis_task.delay(str(analysis.id))
    background_tasks.add_task(
        _run_analysis_background,
        analysis.id,
        db,
        vector_store,
    )

    logger.info(
        "Analysis triggered",
        analysis_id=str(analysis.id),
        repo_id=str(repo.id),
        repo_url=str(request.github_url),
    )

    # Step 4: Return immediately
    return AnalyzeResponse(
        message="Analysis started. Poll the status endpoint for updates.",
        analysis_id=analysis.id,
        repo_id=repo.id,
        status=analysis.status,
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisStatusResponse,
    summary="Get analysis status",
    description="Check the current status and results of an analysis run.",
)
async def get_analysis_status(
    analysis_id: uuid.UUID,
    req: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve the status and results of an analysis.

    Returns the current pipeline stage, and once completed,
    includes entry points, critical files, and summary.
    """
    vector_store = req.app.state.vector_store
    service = AnalysisService(db=db, vector_store=vector_store)
    analysis = await service.get_analysis(analysis_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found",
        )

    return AnalysisStatusResponse(
        analysis_id=analysis.id,
        repo_id=analysis.repo_id,
        status=analysis.status,
        entry_points=analysis.entry_points,
        critical_files=analysis.critical_files,
        summary=analysis.summary,
        error_message=analysis.error_message,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at,
    )
