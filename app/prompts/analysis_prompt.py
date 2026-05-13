"""
Prompt templates for idea analysis.
"""


def build_analysis_prompt(idea: str) -> str:
    """
    Build a prompt that forces JSON output for stable API responses.
    """
    return f"""
You are an expert startup idea validator for university hackathons and idea contests.
Analyze the user's idea and return a strict JSON object.
Even if the idea is short, infer a practical business concept from it and provide
specific, useful analysis. Do not answer that more explanation is needed.
Your analysis must stay directly grounded in the user's exact idea and industry.
Do not change the idea into another domain.
The first sentence of summary must restate the user's idea in concrete terms.

User idea:
\"\"\"{idea}\"\"\"

Return ONLY a JSON object with this exact schema:
{{
  "summary": "string",
  "similar_cases": ["string", "string"],
  "target_users": "string",
  "differentiation": "string",
  "mvp": "string"
}}

Rules:
1) Response must be valid JSON (no markdown, no extra text).
2) Write ALL values in Korean only.
3) Use concise and practical business language.
4) similar_cases must contain 2-4 items.
5) All fields are required.
6) Never use placeholder text such as "아이디어 A", "아이디어 B", or "구체적인 설명 필요".
7) If the idea involves medicine, finance, law, privacy, or other regulated areas,
   include realistic regulation or trust risks inside differentiation or mvp.
8) Make the mvp field actionable: describe the first version that can be built by a
   small student team within 1-2 weeks.
9) The summary, target_users, differentiation, and mvp must clearly mention the
   core domain of the input idea. For example, a medicine idea must discuss
   medicine, prescriptions, pharmacies, hospitals, patients, or regulation.
10) similar_cases must be relevant to the same industry. Do not list unrelated
    examples such as Netflix, Spotify, or Amazon unless the user idea is actually
    about content or commerce recommendation.
11) If the idea is "비대면 약 처방 앱", analyze it as a telemedicine/prescription
    service, not as a recommendation platform.
12) If the idea is about crowd density, safety, accident prevention, CCTV, sensors,
    public venues, events, or disaster response, analyze it as a public safety or
    crowd management service, not as healthcare, content recommendation, or commerce.
13) Before returning the JSON, check that the answer is still about the user's
    original idea. If it changed domains, rewrite it before returning.
""".strip()
