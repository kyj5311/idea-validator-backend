"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="Idea Validation AI Backend",
    description="MVP backend for idea analysis using OpenAI API",
    version="1.0.0",
)

# CORS settings for frontend integration during MVP development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health")
def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "ok"}
