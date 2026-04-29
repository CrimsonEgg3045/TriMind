"""
Explanation Agent — Powered by Groq (LLaMA 3.3 70B)
Generates clear, teacher-style explanations of any topic.
"""

import httpx
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert teacher and study assistant. Your job is to explain concepts clearly and simply.

Rules:
- Explain like you're teaching a curious student who is smart but new to the topic.
- Use simple, everyday language. Avoid heavy jargon.
- Structure your explanation with clear paragraphs.
- Include at least one concrete, relatable example.
- Use analogies when helpful.
- Keep your explanation focused and concise (3-5 paragraphs max).
- Use markdown formatting for readability (bold key terms, use bullet points where helpful).
- Do NOT include math derivations — another agent handles that.
- Do NOT describe visual diagrams — another agent handles that.
"""


async def run(query: str) -> str:
    """Generate a clear explanation for the given query."""
    if not GROQ_API_KEY:
        return "_Explanation agent is not configured (missing GROQ_API_KEY)._"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Explain this concept clearly: {query}"},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
