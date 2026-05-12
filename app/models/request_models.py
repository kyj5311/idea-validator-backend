"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint."""

    idea: str = Field(..., min_length=3, description="User idea text to analyze")


class AnalyzeResponse(BaseModel):
    """Response model for analyzed idea result."""

    summary: str
    similar_cases: list[str]
    target_users: str
    differentiation: str
    mvp: str
