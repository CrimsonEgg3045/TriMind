"""
Explanation Agent — Powered by DeepSeek API
Generates clear, teacher-style explanations with strong intuition-building.
Uses analogies and real-world connections to make concepts accessible.
"""

import httpx
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """You are an exceptional teacher — the kind students remember for years. Your job is to build deep, lasting intuition about any concept.

Rules:
- Explain like a great teacher: start with WHY this concept matters, then HOW it works.
- Use vivid, relatable analogies. Compare abstract ideas to everyday experiences.
- Avoid jargon. If you must use a technical term, immediately explain it in plain language.
- Build intuition step-by-step: start from what the student already knows and gradually introduce new ideas.
- Include at least one concrete, real-world example that makes the concept click.
- Structure your explanation with clear paragraphs and logical flow.
- Use markdown formatting: **bold** key terms, use bullet points where they aid clarity.
- Keep your explanation focused and concise (3-5 paragraphs max).
- Do NOT include mathematical derivations — another agent handles that.
- Do NOT describe visual diagrams — another agent handles that.
- End with a one-sentence "key insight" that captures the essence of the concept.
"""


async def run(query: str) -> str:
    """Generate a clear, intuition-building explanation for the given query."""
    if not DEEPSEEK_API_KEY:
        return "_Explanation agent is not configured (missing DEEPSEEK_API_KEY)._"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Explain this concept clearly, building strong intuition: {query}",
            },
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(DEEPSEEK_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
