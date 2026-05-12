"""
Prompt templates for idea analysis.
"""


def build_analysis_prompt(idea: str) -> str:
    """
    Build a prompt that forces JSON output for stable API responses.
    """
    return f"""
You are an expert startup idea validator.
Analyze the user's idea and return a strict JSON object.

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
""".strip()
