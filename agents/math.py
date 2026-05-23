"""
Math / Derivation Agent — Powered by Google Gemini
Generates step-by-step mathematical derivations and logical reasoning
using the Gemini 2.5 Flash model via the Generative Language REST API.
"""

import httpx
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)

SYSTEM_PROMPT = """\
You are an expert mathematician and rigorous logical thinker.

Your task: given a topic or question, produce a **clear, step-by-step mathematical derivation or logical analysis**.

### Output rules
1. **Structure every response** with numbered steps (Step 1, Step 2, …).
2. **Use LaTeX-style math** delimited by `$` (inline) and `$$` (display).
   - Example inline: $E = mc^2$
   - Example display:
     $$F = ma$$
3. **Never skip steps.** Show every algebraic manipulation, substitution, and simplification.
4. **Explain the reasoning** between steps — state *why* each transformation is valid (cite theorems, identities, or definitions as appropriate).
5. **Include all relevant formulas** and define every variable on first use.
6. If the topic is **not inherently mathematical**, provide a structured logical/analytical breakdown instead (premises → deductions → conclusion).
7. **End with a boxed or highlighted final result** and a one-sentence summary of the key insight.
8. Use **Markdown** formatting (bold, bullets, headers) for readability.
9. Keep the derivation **focused and precise** — aim for clarity, not verbosity.
"""


async def run(query: str) -> str:
    """Generate a step-by-step mathematical derivation for the given query."""
    if not GEMINI_API_KEY:
        return "_Math agent is not configured (missing GEMINI_API_KEY)._"

    url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"{SYSTEM_PROMPT}\n\n---\n\n"
                            f"Provide a step-by-step mathematical derivation or logical analysis for:\n\n{query}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from the Gemini response structure
            candidates = data.get("candidates", [])
            if not candidates:
                return "_Math agent received an empty response from Gemini._"

            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)

            if text.strip():
                return text.strip()
            return "_Math agent received an empty response from Gemini._"

    except httpx.HTTPStatusError as e:
        detail = e.response.text[:200] if e.response else str(e)
        return f"_Math agent encountered an API error: {detail}_"
    except httpx.RequestError as e:
        return f"_Math agent encountered a network error: {str(e)[:150]}_"
    except Exception as e:
        return f"_Math agent encountered an unexpected error: {str(e)[:150]}_"
