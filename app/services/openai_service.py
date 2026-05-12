"""
Service layer for calling OpenAI HTTP API.

MinGW 등 일부 환경에서는 openai 패키지가 끌어오는 jiter(Rust) 빌드가 실패할 수 있어,
Chat Completions REST API를 httpx로 직접 호출합니다. 동작은 동일합니다.
"""

import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

from app.models.request_models import AnalyzeResponse
from app.prompts.analysis_prompt import build_analysis_prompt

# Load .env values once when module is imported.
load_dotenv()

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

class OpenAIAnalysisService:
    """Encapsulates OpenAI interaction for idea analysis."""

    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _require_api_key(self) -> None:
        """Raise HTTP 500 if API key is missing."""
        if not self.api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY is not set. Please check backend/.env",
            )

    def analyze_idea(self, idea: str) -> AnalyzeResponse:
        """
        Call OpenAI Chat Completions with JSON-enforced output and parse safely.
        """
        self._require_api_key()
        prompt = build_analysis_prompt(idea)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise Korean startup idea analyst. "
                        "Return only valid JSON and never drift away from the "
                        "user's actual idea, keywords, or industry."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    OPENAI_CHAT_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            try:
                content = data["choices"][0]["message"]["content"] or "{}"
            except (KeyError, IndexError, TypeError) as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Unexpected OpenAI response shape: {exc}",
                ) from exc

            parsed = json.loads(content)
            return AnalyzeResponse(**parsed)

        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Invalid JSON returned by AI model: {exc}",
            ) from exc
        except httpx.HTTPStatusError as exc:
            # Surface OpenAI error body (truncated) for easier debugging.
            body = ""
            if exc.response is not None:
                try:
                    body = exc.response.text[:500]
                except Exception:
                    body = ""
            raise HTTPException(
                status_code=502,
                detail=f"OpenAI API error ({exc.response.status_code}): {body or exc}",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Network error calling OpenAI: {exc}",
            ) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze idea: {exc}",
            ) from exc


openai_analysis_service = OpenAIAnalysisService()
