"""
services/analysis_service.py - Analysis Orchestrator Service
=============================================================
Orchestrates the full analysis pipeline for a repository.
Coordinates between parser, graph, embedding, and AI services.

Design Note:
    Currently runs in-process via FastAPI BackgroundTasks.
    Designed to be easily migrated to Celery tasks by extracting
    the `run_analysis` method into a Celery task function.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.analysis import Analysis
from models.repo import Repository
from services.parser_service import ParserService
from services.graph_service import GraphService
from services.embedding_service import EmbeddingService
from db.vector_store import VectorStoreManager
from core.constants import AnalysisStatus, ENTRY_POINT_PATTERNS
from core.logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """
    Orchestrates the end-to-end repository analysis pipeline.

    Pipeline stages:
        1. CLONING   → Clone the repo to local filesystem (handled by repo_service)
        2. PARSING   → Parse all source files for structure
        3. ANALYZING → Build dependency graph, detect entry points, find critical files
        4. EMBEDDING → Generate and store vector embeddings for code chunks
        5. COMPLETED → Mark analysis as done

    Migration path to Celery:
        Replace `run_analysis()` with a Celery task decorated with @celery_app.task.
        The method signature and internal logic remain the same.
    """

    def __init__(
        self,
        db: AsyncSession,
        vector_store: VectorStoreManager,
    ):
        self.db = db
        self.vector_store = vector_store

    async def create_analysis(self, repo_id: uuid.UUID) -> Analysis:
        """
        Create a new Analysis record in PENDING status.
        Called before dispatching the background task.
        """
        analysis = Analysis(
            repo_id=repo_id,
            status=AnalysisStatus.PENDING,
        )
        self.db.add(analysis)
        await self.db.flush()
        logger.info("Analysis created", analysis_id=str(analysis.id), repo_id=str(repo_id))
        return analysis

    async def run_analysis(self, analysis_id: uuid.UUID) -> None:
        """
        Execute the full analysis pipeline.

        This method is designed to run as a BackgroundTask.
        Each stage updates the analysis status in the database.

        Args:
            analysis_id: The UUID of the analysis record to process.
        """
        # Re-fetch analysis within this context
        result = await self.db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            logger.error("Analysis not found", analysis_id=str(analysis_id))
            return

        # Fetch associated repository
        repo_result = await self.db.execute(
            select(Repository).where(Repository.id == analysis.repo_id)
        )
        repo = repo_result.scalar_one_or_none()
        if not repo or not repo.clone_path:
            await self._fail_analysis(analysis, "Repository not found or not cloned")
            return

        try:
            # --- Stage 1: PARSING ---
            analysis.status = AnalysisStatus.PARSING
            await self.db.commit()

            parser = ParserService(repo.clone_path)
            files = parser.get_all_files()

            # Parse each file for structure
            parsed_structures = {}
            for file_info in files:
                if file_info["language"] == "python":
                    parsed_structures[file_info["relative_path"]] = (
                        parser.parse_python_file(file_info["path"])
                    )

            # Update repo file stats
            repo.total_files = len(files)
            repo.total_lines = sum(f.get("line_count", 0) for f in files)

            # --- Stage 2: ANALYZING ---
            analysis.status = AnalysisStatus.ANALYZING
            await self.db.commit()

            # Build dependency graph
            graph_service = GraphService()
            graph_service.build_from_parsed_data(files, parsed_structures)

            # Detect entry points
            entry_points = self._detect_entry_points(files)
            analysis.entry_points = entry_points

            # Identify critical files
            critical_files = graph_service.get_critical_files(top_n=10)
            analysis.critical_files = critical_files

            # Store graph metadata
            analysis.graph_data = graph_service.serialize_graph()

            # --- Stage 3: EMBEDDING ---
            analysis.status = AnalysisStatus.EMBEDDING
            await self.db.commit()

            embedding_service = EmbeddingService(self.vector_store)
            await embedding_service.embed_repository(
                repo_id=repo.id,
                repo_path=repo.clone_path,
                files=files,
            )

            # --- Complete ---
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.now(timezone.utc)
            await self.db.commit()

            logger.info(
                "Analysis completed successfully",
                analysis_id=str(analysis_id),
                total_files=len(files),
            )

        except Exception as e:
            logger.exception("Analysis failed", analysis_id=str(analysis_id))
            await self._fail_analysis(analysis, str(e))

    async def get_analysis(self, analysis_id: uuid.UUID) -> Analysis | None:
        """Retrieve an analysis by ID."""
        result = await self.db.execute(
            select(Analysis).where(Analysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_analysis(self, repo_id: uuid.UUID) -> Analysis | None:
        """Get the most recent analysis for a repository."""
        result = await self.db.execute(
            select(Analysis)
            .where(Analysis.repo_id == repo_id)
            .order_by(Analysis.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    def _detect_entry_points(self, files: list[dict]) -> list[str]:
        """Detect likely entry point files based on naming patterns."""
        entry_points = []
        for f in files:
            filename = f["relative_path"].split("/")[-1]
            if filename in ENTRY_POINT_PATTERNS:
                entry_points.append(f["relative_path"])
        return entry_points

    async def _fail_analysis(self, analysis: Analysis, error_msg: str) -> None:
        """Mark an analysis as failed with an error message."""
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = error_msg
        analysis.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        logger.error("Analysis marked as failed", analysis_id=str(analysis.id), error=error_msg)
