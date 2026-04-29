"""
Math / Derivation Agent — Powered by OpenRouter
Generates step-by-step mathematical derivations and logical reasoning.

Model cascade (tries each in order until one succeeds):
  1. openai/gpt-oss-20b:free      — primary (fast, reliable)
  2. nvidia/nemotron-3-super-120b-a12b:free — large reasoning model
  3. openai/gpt-oss-120b:free     — largest free fallback
  4. google/gemma-3-27b-it:free   — last resort (often rate-limited)
"""

import asyncio
import httpx
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ordered list of models to try — first working one wins
MODEL_CASCADE = [
    "openai/gpt-oss-20b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-3-27b-it:free",
]

# Error codes that mean "this model won't work right now, try the next one"
FALLBACK_CODES = {429, 402, 503, 529}

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


async def _try_model(client: httpx.AsyncClient, model: str, payload: dict, headers: dict) -> str | None:
    """
    Attempt a single model. Returns the text content on success, or None if
    the model is unavailable (rate-limited / quota exceeded). Raises on hard errors.
    """
    body = {**payload, "model": model}
    for attempt in range(2):  # up to 2 retries per model for transient 429s
        response = await client.post(OPENROUTER_URL, json=body, headers=headers)
        if response.status_code in FALLBACK_CODES:
            if attempt == 0:
                await asyncio.sleep(2 ** attempt)
                continue
            return None  # give up on this model, cascade to next
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if content:
            return content
        return None  # empty response — try next model
    return None


async def run(query: str) -> str:
    """Generate a step-by-step mathematical derivation for the given query."""
    if not OPENROUTER_API_KEY:
        return "_Math agent is not configured (missing OPENROUTER_API_KEY)._"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://study-assistant.app",
        "X-Title": "Tri Mind Study Assistant",
    }

    payload = {
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

    last_error: Exception | None = None

    async with httpx.AsyncClient(timeout=45.0) as client:
        for model in MODEL_CASCADE:
            try:
                result = await _try_model(client, model, payload, headers)
                if result is not None:
                    return result
                # result is None → model unavailable, try next in cascade
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code not in FALLBACK_CODES:
                    break  # hard error — don't continue cascade
            except httpx.RequestError as e:
                last_error = e
                break  # network error — don't loop endlessly

    error_detail = str(last_error)[:150] if last_error else "all models unavailable"
    return f"_Math agent encountered an error: {error_detail}_"
