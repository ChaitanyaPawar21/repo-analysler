"""
schemas/chat_schema.py - Chat Pydantic Schemas
================================================
Request and response schemas for the AI chat interface over codebases.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# =============================================================================
# Request Schemas
# =============================================================================

class ChatRequest(BaseModel):
    """Schema for sending a chat message about a repository."""
    repo_id: uuid.UUID = Field(
        ...,
        description="ID of the repository to query against.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's question or prompt about the codebase.",
        examples=["What does the main entry point do?"],
    )
    conversation_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional conversation ID for multi-turn chat context.",
    )


class ChatResponse(BaseModel):
    """Schema for AI chat response."""
    conversation_id: uuid.UUID
    message: str = Field(..., description="AI-generated response.")
    sources: List["ChatSource"] = Field(
        default_factory=list,
        description="Source code chunks referenced in the answer.",
    )


class ChatSource(BaseModel):
    """A source code reference cited in the AI response."""
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: str = Field(..., description="Relevant code snippet.")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score from vector search.",
    )


# Rebuild model to resolve forward references
ChatResponse.model_rebuild()
