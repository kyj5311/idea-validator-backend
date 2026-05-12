#AI로 아이디어 검증 과정을 없앤다면?(백엔드 작업물)

##FastAPI AI 아이디어 검증 백엔드 (MVP)
이 프로젝트는 멋쟁이사자처럼 대학 아이디어톤 대회 프로덕트 백엔드 부분입니다.
사용자가 아이디어를 입력하면 OpenAI API를 통해 분석한 결과를 JSON으로 반환하는 최소 기능을 수행합니다.

인수인계 참고 문서: `HANDOFF.md`

## 1) 프로젝트 구조

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
 └── README.md
```

## 2) 설치 및 실행

### (0) 사용할 Python (필독)

이 백엔드는 **python.org Windows용 CPython**으로 만든 가상환경을 권장합니다. **버전은 3.12 또는 3.13 64-bit**가 무난합니다.

**MSYS2 / MinGW Python**(`C:\msys64\...`, 가상환경에 `Scripts` 대신 `.venv\bin`만 생기는 경우 등)은 PyPI에 맞는 **미리 빌드된 휠이 거의 없어** `pydantic-core`, 예전 `jiter` 등에서 `pip install`이 계속 실패할 수 있습니다. 그런 증상이면 아래처럼 **공식 Python을 설치한 뒤 venv를 새로 만드는 것**이 정답에 가깝습니다.

1. [python.org](https://www.python.org/downloads/)에서 **Python 3.12 (Windows installer 64-bit)** 설치  
2. 설치 화면에서 **Add python.exe to PATH** 체크  
3. 기존 가상환경 삭제 후 재생성:

```powershell
cd C:\workspace\backend
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

`py` 명령이 없으면 시작 메뉴의 **Python 3.12** 설치 경로(예: `C:\Users\<사용자>\AppData\Local\Programs\Python\Python312\python.exe`)를 찾아 동일하게 `-m venv .venv`를 실행하면 됩니다. 활성화 후 프롬프트 앞에 `(.venv)`가 보이고, 폴더에 **`.venv\Scripts\python.exe`**가 있으면 올바른 환경입니다.

### (1) 가상환경 생성/활성화 (선택)

Windows PowerShell(공식 Python 기준):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### (2) 패키지 설치

```powershell
pip install -r requirements.txt
```

### (3) .env 설정

먼저 `.env.example`을 복사해 `.env`를 만들고, 실제 키(OPENAI_API_KEY)를 입력합니다.

```powershell
copy .env.example .env
```

`backend/.env` 파일에 OpenAI API Key를 입력합니다.

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### (4) 서버 실행

`backend` 폴더에서 실행:

```powershell
uvicorn app.main:app --reload
```

서버 기본 주소: `http://127.0.0.1:8000`

## 3) API 사용법

### POST `/analyze`

요청 예시:

```json
{
  "idea": "공모전 아이디어 검증 AI 서비스"
}
```

응답 예시:

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

## 4) 구현 포인트

- FastAPI 기반 단일 핵심 엔드포인트(`/analyze`) 제공
- OpenAI Chat Completions를 `httpx`로 호출 (일부 Python/MinGW 환경에서 `openai` 패키지의 Rust 의존성 빌드 실패를 피하기 위함)
- OpenAI 응답을 JSON으로 강제하도록 프롬프트 + `response_format` 적용
- `.env`를 통한 API Key/모델 관리
- CORS 허용 설정 포함
- 에러 처리 포함 (입력 오류/AI 응답 파싱 오류/일반 예외)

## 5) 현재 범위 (MVP)

현재는 아래 핵심 흐름만 구현되어 있습니다.

`아이디어 입력 -> AI 분석 -> 결과 JSON 반환`

로그인, DB, JWT, Redis, RAG, Docker 등은 의도적으로 제외했습니다.
