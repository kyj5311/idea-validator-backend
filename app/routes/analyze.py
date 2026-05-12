"""
API routes for idea analysis.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.request_models import AnalyzeRequest, AnalyzeResponse
from app.services.openai_service import openai_analysis_service

router = APIRouter(prefix="", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_idea(request: AnalyzeRequest) -> JSONResponse:
    """
    Analyze a user idea and return structured JSON response.
    """
    idea = request.idea.strip()
    if not idea:
        raise HTTPException(status_code=400, detail="idea cannot be empty")

    result = openai_analysis_service.analyze_idea(idea)
    # Explicitly set UTF-8 charset for PowerShell/Windows clients.
    return JSONResponse(
        content=result.model_dump(),
        media_type="application/json; charset=utf-8",
    )
