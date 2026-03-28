"""
main.py - FastAPI Application Entry Point
==========================================
Initializes the FastAPI application, registers routers, configures middleware,
and sets up application lifecycle events (startup/shutdown).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import setup_logging, get_logger
from api.v1.router import api_v1_router
from db.postgres import engine, async_session_factory, init_db
from db.vector_store import VectorStoreManager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup initialization and graceful shutdown of resources.
    """
    # --- Startup ---
    setup_logging()
    logger.info("Starting Repo Analyser API", version="1.0.0", env=settings.APP_ENV)

    # Initialize PostgreSQL tables
    await init_db()
    logger.info("PostgreSQL database initialized")

    # Initialize FAISS vector store
    vector_store = VectorStoreManager()
    vector_store.initialize()
    app.state.vector_store = vector_store
    logger.info("FAISS vector store initialized")

    yield  # Application is running

    # --- Shutdown ---
    logger.info("Shutting down Repo Analyser API")
    await engine.dispose()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    Using a factory pattern allows easy testing and multiple configurations.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="GitHub Repository Analysis Platform — analyze structure, "
                    "build dependency graphs, detect entry points, and chat with codebases.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Register API Routers ---
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


# Create the app instance
app = create_application()


@app.get("/health", tags=["Health"])
async def health_check():
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }
