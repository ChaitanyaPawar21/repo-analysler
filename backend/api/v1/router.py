"""
api/v1/router.py - API v1 Router Aggregator
=============================================
Aggregates all v1 endpoint routers into a single router.
This is the single entry point registered in main.py.
"""

from fastapi import APIRouter

from api.v1.endpoints import analyze, repo, chat, graph, critical_files

api_v1_router = APIRouter()

# --- Register all endpoint routers ---

api_v1_router.include_router(
    repo.router,
    prefix="/repos",
    tags=["Repositories"],
)

api_v1_router.include_router(
    analyze.router,
    prefix="/analyze",
    tags=["Analysis"],
)

api_v1_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)

api_v1_router.include_router(
    graph.router,
    prefix="/graph",
    tags=["Dependency Graph"],
)

api_v1_router.include_router(
    critical_files.router,
    prefix="/critical-files",
    tags=["Critical Files"],
)
