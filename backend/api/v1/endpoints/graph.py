"""
api/v1/endpoints/graph.py - Dependency Graph Endpoints
=======================================================
Endpoints for retrieving and exploring repository dependency graphs.
Provides full graph data and localized subgraph views.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db_session
from services.analysis_service import AnalysisService
from services.graph_service import GraphService
from core.constants import AnalysisStatus
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/{repo_id}",
    summary="Get full dependency graph",
    description="Retrieve the complete dependency graph for an analyzed repository.",
)
async def get_dependency_graph(
    repo_id: uuid.UUID,
    req: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Return the full dependency graph for a repository.

    The graph includes:
        - nodes: files with metadata (language, line count)
        - edges: import/dependency relationships
        - summary statistics (total nodes, total edges)

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
            detail=f"Analysis is not completed yet. Current status: {analysis.status}",
        )

    if not analysis.graph_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Graph data not available for this analysis",
        )

    return {
        "repo_id": str(repo_id),
        "analysis_id": str(analysis.id),
        "graph": analysis.graph_data,
    }


@router.get(
    "/{repo_id}/subgraph",
    summary="Get localized subgraph",
    description="Retrieve a subgraph centered on a specific file node.",
)
async def get_subgraph(
    repo_id: uuid.UUID,
    node_id: str = Query(..., description="File path of the center node"),
    depth: int = Query(2, ge=1, le=5, description="Traversal depth from center node"),
    req: Request = None,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get a localized view of the dependency graph centered on a specific file.

    Useful for:
        - Understanding a file's direct and transitive dependencies.
        - Visualizing the impact radius of a file change.
    """
    vector_store = req.app.state.vector_store
    service = AnalysisService(db=db, vector_store=vector_store)
    analysis = await service.get_latest_analysis(repo_id)

    if not analysis or analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completed analysis not found for this repository",
        )

    if not analysis.graph_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Graph data not available",
        )

    # Reconstruct graph from stored data and extract subgraph
    graph_service = GraphService()
    # Re-populate the graph from stored nodes/edges
    for node in analysis.graph_data.get("nodes", []):
        node_id_val = node.pop("id", None)
        if node_id_val:
            graph_service.graph.add_node(node_id_val, **node)

    for edge in analysis.graph_data.get("edges", []):
        source = edge.pop("source", None)
        target = edge.pop("target", None)
        if source and target:
            graph_service.graph.add_edge(source, target, **edge)

    subgraph = graph_service.get_subgraph(node_id, depth=depth)

    return {
        "repo_id": str(repo_id),
        "center_node": node_id,
        "depth": depth,
        "subgraph": subgraph,
    }
