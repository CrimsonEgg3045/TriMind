"""
Math / Derivation Agent — Powered by OpenRouter (Gemma 3 27B Free)
Generates step-by-step mathematical derivations and logical reasoning.
"""

import httpx
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemma-3-27b-it:free"

SYSTEM_PROMPT = """You are a brilliant mathematician and logical thinker. Your job is to provide step-by-step mathematical derivations and logical reasoning.

Rules:
- Provide clear, step-by-step derivations. Never skip steps.
- Use proper mathematical notation (you can use LaTeX-style notation with $ delimiters).
- Label each step clearly (Step 1, Step 2, etc.).
- Show the logical progression from assumptions to conclusions.
- Include relevant formulas and equations.
- Explain WHY each step follows from the previous one.
- If the topic isn't inherently mathematical, provide logical/analytical reasoning instead.
- Use markdown formatting for readability.
- Keep derivations focused — aim for clarity over exhaustiveness.
- End with a concise summary of the key mathematical result.
"""


async def run(query: str) -> str:
    """Generate a step-by-step mathematical derivation for the given query."""
    if not OPENROUTER_API_KEY:
        return "_Math agent is not configured (missing OPENROUTER_API_KEY)._"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://study-assistant.app",
        "X-Title": "Multi-Agent Study Assistant",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Provide a step-by-step mathematical derivation or logical analysis for: {query}",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 1500,
    }

    import asyncio

    async with httpx.AsyncClient(timeout=45.0) as client:
        last_error = None
        for attempt in range(3):
            try:
                response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
                if response.status_code == 429:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code != 429:
                    break
                await asyncio.sleep(2 ** attempt)
        return f"_Math agent encountered an error: {str(last_error)[:150]}_"
