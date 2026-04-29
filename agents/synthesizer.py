"""
Final Synthesizer Agent — Powered by Groq (LLaMA 3.3 70B)
Combines outputs from all agents into one structured, polished response.
Preserves the math agent's derivation faithfully.
"""

import httpx
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a master study tutor and content synthesizer. You receive outputs from three specialized AI agents and must combine them into ONE polished, structured study response.

CRITICAL RULES:

1. Format the final response into these sections:

## 📖 Simple Explanation
(Rewrite the explanation agent's output — make it cleaner and more concise if needed. Use simple language.)

## 🔢 Mathematical Derivation
(IMPORTANT: Include the math agent's derivation EXACTLY as provided. Do NOT simplify, paraphrase, or skip any mathematical steps. Preserve all formulas, equations, step numbering, and LaTeX notation verbatim. You may only fix formatting issues or add very minor clarifying transitions between steps. The math content must remain faithful to the original.)

## 🎨 Visual Understanding
(Include the visual agent's diagram descriptions — format them cleanly)

2. Additional rules:
- Maintain a warm, tutor-like tone throughout.
- Use markdown formatting for readability.
- Add a brief 1-2 sentence introduction before the sections.
- Add a brief "💡 Key Takeaway" at the end summarizing the core idea in one sentence.
- If any section's input is missing or says "unavailable", write a brief helpful note instead of leaving it empty.
- NEVER modify or simplify the math derivation steps. Include them as-is.
"""


async def run(
    query: str,
    explanation: str,
    math_result: str,
    visual_result: str,
) -> str:
    """Synthesize all agent outputs into one structured response."""
    if not GROQ_API_KEY:
        return _manual_synthesis(explanation, math_result, visual_result)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    user_message = f"""Original Question: {query}

--- EXPLANATION AGENT OUTPUT ---
{explanation}

--- MATH AGENT OUTPUT (INCLUDE VERBATIM — DO NOT MODIFY THE MATH) ---
{math_result}

--- VISUAL AGENT OUTPUT ---
{visual_result}

Please synthesize these into one structured study response. Remember: the math derivation must be included exactly as provided, do not simplify or skip any steps."""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.4,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(GROQ_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _manual_synthesis(explanation: str, math_result: str, visual_result: str) -> str:
    """Fallback: manually combine outputs without an API call."""
    return f"""## 📖 Simple Explanation

{explanation}

---

## 🔢 Mathematical Derivation

{math_result}

---

## 🎨 Visual Understanding

{visual_result}
"""
