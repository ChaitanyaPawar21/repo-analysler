"""
api/v1/endpoints/chat.py - Chat Endpoints
==========================================
AI-powered chat interface for querying analyzed codebases.
Uses RAG (Retrieval-Augmented Generation) over FAISS-indexed code chunks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db_session
from services.ai_service import AIService
from services.repo_service import RepoService
from schemas.chat_schema import ChatRequest, ChatResponse
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Chat with a codebase",
    description="Ask questions about an analyzed repository using AI.",
)
async def chat_with_codebase(
    request: ChatRequest,
    req: Request,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Send a natural language question about a repository's codebase.

    The AI will:
        1. Search the vector store for relevant code chunks.
        2. Build a context-enriched prompt.
        3. Generate a response with source attributions.

    Prerequisites:
        - The repository must have been analyzed (status: COMPLETED).
        - Embeddings must exist in the FAISS vector store.
    """
    # Verify the repository exists
    repo_service = RepoService(db)
    repo = await repo_service.get_by_id(request.repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository {request.repo_id} not found",
        )

    # Initialize AI service with vector store
    vector_store = req.app.state.vector_store
    ai_service = AIService(vector_store=vector_store)

    try:
        response = await ai_service.chat(
            repo_id=request.repo_id,
            user_message=request.message,
        )
        return response
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Chat request failed", repo_id=str(request.repo_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your chat request.",
        )
