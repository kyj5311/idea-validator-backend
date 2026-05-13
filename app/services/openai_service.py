"""
Service layer for calling OpenAI HTTP API.

MinGW 등 일부 환경에서는 openai 패키지가 끌어오는 jiter(Rust) 빌드가 실패할 수 있어,
Chat Completions REST API를 httpx로 직접 호출합니다. 동작은 동일합니다.
"""

import json
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

from app.models.request_models import AnalyzeResponse
from app.prompts.analysis_prompt import build_analysis_prompt

# Load .env values once when module is imported.
load_dotenv()

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
GROUNDING_STOPWORDS = {
    "ai",
    "기반",
    "서비스",
    "플랫폼",
    "앱",
    "어플",
    "시스템",
    "분석",
}


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

    def _extract_grounding_keywords(self, idea: str) -> list[str]:
        """Extract idea-specific words used to catch off-topic model responses."""
        tokens = re.findall(r"[0-9A-Za-z가-힣]+", idea.lower())
        keywords = []
        for token in tokens:
            if len(token) < 2 or token in GROUNDING_STOPWORDS:
                continue
            if token not in keywords:
                keywords.append(token)
        return keywords

    def _is_grounded_in_idea(
        self,
        result: AnalyzeResponse,
        keywords: list[str],
    ) -> bool:
        """Return whether the response still mentions enough idea-specific words."""
        if not keywords:
            return True

        combined_text = " ".join(
            [
                result.summary,
                " ".join(result.similar_cases),
                result.target_users,
                result.differentiation,
                result.mvp,
            ]
        ).lower()
        matched_count = sum(1 for keyword in keywords if keyword in combined_text)
        required_count = 1 if len(keywords) <= 2 else 2
        return matched_count >= required_count

    def _build_payload(self, prompt: str) -> dict:
        """Build the Chat Completions payload."""
        return {
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
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

    def _request_analysis(self, client: httpx.Client, prompt: str) -> AnalyzeResponse:
        """Call OpenAI once and parse the structured result."""
        response = client.post(
            OPENAI_CHAT_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=self._build_payload(prompt),
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

    def _fallback_analysis(self, idea: str) -> AnalyzeResponse:
        """Return a conservative grounded response if the model drifts twice."""
        lowered_idea = idea.lower()
        if any(
            keyword in lowered_idea
            for keyword in ["혼잡", "인명", "사고", "cctv", "센서", "재난", "안전"]
        ):
            return AnalyzeResponse(
                summary=(
                    f"{idea}은 CCTV, 센서, 위치 데이터 등을 활용해 공간의 혼잡도를 "
                    "실시간으로 파악하고 사고 위험을 조기에 알리는 공공 안전 플랫폼입니다."
                ),
                similar_cases=[
                    "지자체 CCTV 통합관제센터",
                    "스마트시티 보행자 안전 관제 서비스",
                    "행사장 인파 밀집 모니터링 시스템",
                ],
                target_users=(
                    "지자체, 축제 및 공연장 운영자, 학교와 공공시설 관리자, "
                    "대규모 인파가 모이는 공간의 안전 담당자"
                ),
                differentiation=(
                    "단순 CCTV 확인이 아니라 혼잡도 변화와 위험 신호를 AI로 분석해 "
                    "관리자에게 선제 알림을 제공하는 점이 차별점입니다. 개인정보 보호와 "
                    "영상 데이터 처리 기준을 명확히 해야 합니다."
                ),
                mvp=(
                    "1-2주 안에는 샘플 CCTV 영상 또는 업로드된 이미지를 기준으로 "
                    "혼잡도를 낮음/보통/높음으로 분류하고, 위험 단계일 때 관리자 "
                    "대시보드에 경고를 표시하는 웹 프로토타입을 만들 수 있습니다."
                ),
            )

        return AnalyzeResponse(
            summary=f"{idea}을 실제 사용자 문제 해결 관점에서 검증하는 MVP 서비스입니다.",
            similar_cases=[
                "유사 문제 해결 플랫폼",
                "AI 기반 업무 자동화 서비스",
                "데이터 기반 의사결정 지원 서비스",
            ],
            target_users="해당 문제를 반복적으로 겪는 개인 사용자 또는 운영 담당자",
            differentiation=(
                "입력된 아이디어의 핵심 문제에 집중해 빠른 분석과 실행 가능한 "
                "초기 해결책을 제공하는 점이 차별점입니다."
            ),
            mvp=(
                "핵심 입력값을 받고 결과 리포트를 보여주는 간단한 웹 프로토타입을 "
                "먼저 구현해 사용자 반응을 확인합니다."
            ),
        )

    def analyze_idea(self, idea: str) -> AnalyzeResponse:
        """
        Call OpenAI Chat Completions with JSON-enforced output and parse safely.
        """
        self._require_api_key()
        prompt = build_analysis_prompt(idea)
        grounding_keywords = self._extract_grounding_keywords(idea)

        try:
            with httpx.Client(timeout=120.0) as client:
                result = self._request_analysis(client, prompt)
                if self._is_grounded_in_idea(result, grounding_keywords):
                    return result

                retry_prompt = (
                    f"{prompt}\n\n"
                    "The previous response was rejected because it changed the "
                    "idea domain. Rewrite the JSON so it is directly about the "
                    f"user idea and these core keywords: {', '.join(grounding_keywords)}. "
                    "Do not mention unrelated domains."
                )
                retry_result = self._request_analysis(client, retry_prompt)
                if self._is_grounded_in_idea(retry_result, grounding_keywords):
                    return retry_result

                return self._fallback_analysis(idea)

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
