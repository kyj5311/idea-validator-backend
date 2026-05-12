# HANDOFF.md

## 1) 프로젝트 목적

아이디어톤 MVP 백엔드입니다.  
핵심 목표는 아래 단일 흐름입니다.

`아이디어 입력 -> OpenAI 분석 -> 결과 JSON 반환`

복잡 기능(로그인, DB, JWT, Redis, RAG, Docker)은 현재 범위에서 제외했습니다.

---

## 2) 현재 완료 범위

- FastAPI 서버 구성 완료
- `POST /analyze` 엔드포인트 구현 완료
- OpenAI API 연동 완료 (`httpx`로 REST 호출, `.env` 기반 API Key)
- 응답 JSON 구조 고정
- 프론트 연동 기준 Request/Response 필드명 고정
- 짧은 입력에서도 입력 도메인을 벗어나지 않도록 프롬프트 보강
- placeholder 응답 방지 규칙 추가
- CORS 허용 설정 완료
- 기본 에러 처리 포함
- `README.md`에 실행/테스트 방법 정리 완료

---

## 3) 코드 구조

```text
backend/
 ├── app/
 │    ├── main.py
 │    ├── routes/
 │    │     └── analyze.py
 │    ├── services/
 │    │     └── openai_service.py
 │    ├── models/
 │    │     └── request_models.py
 │    └── prompts/
 │          └── analysis_prompt.py
 │
 ├── requirements.txt
 ├── .env
 ├── README.md
 └── HANDOFF.md
```

---

## 4) API 계약 (프론트 연동 기준)

### Endpoint

- `POST /analyze`

### Request Body

```json
{
  "idea": "공모전 아이디어 검증 AI 서비스"
}
```

### Success Response (`200`)

```json
{
  "summary": "AI 기반 아이디어 검증 및 리서치 통합 서비스",
  "similar_cases": [
    "AI 시장 조사 플랫폼",
    "스타트업 아이디어 검증 서비스"
  ],
  "target_users": "공모전 및 해커톤을 준비하는 대학생",
  "differentiation": "대학생 공모전 환경에 특화된 빠른 아이디어 검증 제공",
  "mvp": "아이디어 입력 후 유사 사례와 차별화 포인트를 리포트 형태로 제공"
}
```

### Error Response 형식

FastAPI 기본 형식으로 반환됩니다.

```json
{
  "detail": "에러 메시지"
}
```

주요 케이스:

- `400`: `idea`가 공백인 경우
- `500`: 서버 내부 오류 / OpenAI 키 누락 / OpenAI 호출 실패
- `502`: AI 응답 JSON 파싱 실패

---

## 5) 프론트팀 공유용 고정 규칙

아래 요청/응답 키는 프론트 구현 기준으로 **고정** 사용합니다.

Request:

- `idea`

Response:

- `summary`
- `similar_cases` (배열)
- `target_users`
- `differentiation`
- `mvp`

필드명 변경 시 프론트 파싱 코드도 함께 수정되어야 하므로, 변경 전 팀 합의가 필요합니다.  
후속 백엔드 작업에서는 내부 로직, 프롬프트, 에러 처리 개선은 가능하지만 위 API 계약은 유지하는 것을 기본 원칙으로 합니다.

---

## 6) 주요 코드 위치

- 서버 진입점/CORS/헬스체크: `app/main.py`
- `/analyze` 라우터: `app/routes/analyze.py`
- Request/Response 모델: `app/models/request_models.py`
- OpenAI REST 호출 및 에러 처리: `app/services/openai_service.py`
- 분석 프롬프트: `app/prompts/analysis_prompt.py`

---

## 7) 로컬 실행 방법

`backend` 폴더에서:

1. `pip install -r requirements.txt`
2. `.env` 설정
   - `OPENAI_API_KEY=...` (필수)
   - `OPENAI_MODEL=gpt-4o-mini` (선택)
3. `uvicorn app.main:app --reload`

기본 주소: `http://127.0.0.1:8000`

---

## 8) 빠른 테스트 (스모크)

정상 케이스:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"idea\":\"공모전 아이디어 검증 AI 서비스\"}"
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/analyze" -ContentType "application/json" -Body '{"idea":"공모전 아이디어 검증 AI 서비스"}' | ConvertTo-Json -Depth 5
```

실패 케이스 (공백 입력):

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"idea\":\"   \"}"
```

---

## 9) GitHub에서 받은 뒤 테스트하는 순서

후속 백엔드 담당자가 저장소를 새로 받은 뒤에는 아래 순서로 확인하면 됩니다.

1. 프로젝트 받기

```powershell
git clone https://github.com/kyj5311/idea-validator-backend.git
cd idea-validator-backend
```

2. 가상환경 생성/활성화

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

`py` 명령이 없으면 아래 명령으로 시도합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 환경변수 파일 준비

```powershell
copy .env.example .env
```

`.env` 파일을 열어서 실제 키를 입력합니다.

```env
OPENAI_API_KEY=sk-본인키
OPENAI_MODEL=gpt-4o-mini
```

4. 패키지 설치

```powershell
python -m pip install -r requirements.txt
```

5. 서버 실행

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

정상 실행 기준:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

6. API 테스트

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/analyze" -ContentType "application/json" -Body '{"idea":"바퀴가 3개인 자동차"}' | ConvertTo-Json -Depth 5
```

7. 성공 기준

응답에 아래 필드가 모두 나오면 성공입니다.

- `summary`
- `similar_cases`
- `target_users`
- `differentiation`
- `mvp`

---

## 10) 자주 나는 에러 빠른 대응

| 증상 | 가능한 원인 | 대응 |
| --- | --- | --- |
| `401 invalid_api_key` | `.env`의 OpenAI API Key가 잘못됨 | 키가 실제 발급 키인지, 공백/따옴표가 섞이지 않았는지 확인 |
| `429 insufficient_quota` | OpenAI 크레딧 또는 요금제 문제 | OpenAI 계정의 결제/사용량 상태 확인 |
| `Could not connect to server` | uvicorn 서버가 실행되지 않았거나 종료됨 | 서버 실행 터미널에서 `uvicorn` 로그 확인 |
| `OPENAI_API_KEY is not set` | `.env`가 없거나 키 이름이 틀림 | `.env.example`을 복사해 `.env` 생성 후 `OPENAI_API_KEY` 입력 |
| `pip install` 실패 | MSYS2/MinGW Python 또는 지원되지 않는 Python 버전 사용 | python.org CPython 3.12/3.13으로 가상환경 재생성 |

---

## 11) 알려진 한계 / 리스크

- **MSYS2/MinGW Python + 최신 마이너(예: 3.14)** 로는 `pydantic-core` 등 휠이 없어 `pip install`이 실패할 수 있음 → **python.org Windows CPython 3.12/3.13** 권장 (`README.md` (0)절 참고)
- OpenAI 응답 품질은 입력 문장에 따라 편차가 있을 수 있음. 현재는 프롬프트에서 도메인 이탈과 placeholder 응답을 줄이도록 보강한 상태
- 외부 API(OpenAI) 장애/지연 시 응답 지연 가능
- 현재는 로깅/모니터링이 최소 수준
- 현재 에러 메시지는 개발 편의 중심 (운영 시 메시지 정제 필요)

---

## 12) 다음 백엔드 담당자 우선 TODO

1. 프론트와 실제 연동 후 CORS `allow_origins`를 실제 도메인으로 제한
2. 타임아웃/재시도 정책 정리 (OpenAI 요청 안정화)
3. 에러 코드/메시지 규약 확정 (프론트 에러 UX와 맞춤)
4. 테스트 코드 추가 (최소: `/analyze` 정상/실패 케이스)
5. 운영 환경용 `.env` 관리 정책 정리 (비밀키 누출 방지)

---

## 13) 변경 시 주의사항

- MVP 목적상 구조를 단순하게 유지하는 것이 우선입니다.
- 로그인/DB/JWT/Redis/RAG 등 범위 외 기능은 별도 합의 후 진행 권장.
- 프론트 연동 직전에는 반드시 API 응답 필드 호환성을 다시 확인하세요.
- `summary`, `similar_cases`, `target_users`, `differentiation`, `mvp` 필드명은 프론트 연동 기준이므로 임의 변경하지 마세요.

---

## 14) 인수인계 마무리 체크리스트

1. `.env`가 Git에 포함되지 않았는지 확인
2. `.env.example`에는 실제 키가 아닌 예시값만 남아 있는지 확인
3. `.gitignore`에 `.env`, `.venv`가 포함되어 있는지 확인
4. `README.md`, `HANDOFF.md`, `.env.example` 기준으로 실행/전달 자료 최종 점검
5. `POST /analyze` 스모크 테스트 성공 로그 1회 확인
6. 응답에 고정 필드가 모두 포함되는지 확인
   - `summary`
   - `similar_cases`
   - `target_users`
   - `differentiation`
   - `mvp`
7. 프론트와 합의한 API 계약이 바뀌지 않았는지 확인
   - Request: `{ "idea": "string" }`
   - Response keys: `summary`, `similar_cases`, `target_users`, `differentiation`, `mvp`
8. 후속 백엔드 담당자에게 9번 섹션의 GitHub 클론 후 테스트 절차와 10번 섹션의 자주 나는 에러 대응을 함께 안내
9. 프론트팀/백엔드 후속 담당자에게 아래 템플릿으로 전달

### 프론트팀 전달 템플릿

```text
[백엔드 API 전달]
- Endpoint: POST /analyze
- Request: { "idea": "string" }
- Response keys (고정): summary, similar_cases, target_users, differentiation, mvp
- Error format: { "detail": "..." }
- 테스트 주소(로컬): http://127.0.0.1:8000/analyze
- 비고: 필드명 변경 시 사전 합의 필요
```

### 백엔드 후속 담당자 전달 템플릿

```text
[백엔드 인수인계]
- 실행 기준 문서: README.md
- 상세 인수인계: HANDOFF.md
- 환경변수 템플릿: .env.example (.env는 커밋 금지)
- 현재 완료 범위: 아이디어 입력 -> AI 분석 -> JSON 반환
- 로컬 재현 절차: HANDOFF.md 9번 섹션 참고
- 자주 나는 에러 대응: HANDOFF.md 10번 섹션 참고
- 우선 TODO: CORS 도메인 제한, 에러 규약 정리, 테스트 코드 추가
```
