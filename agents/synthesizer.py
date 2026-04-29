"""
Final Synthesis Agent — Powered by DeepSeek API
Acts as an INTELLIGENT ORCHESTRATOR (not a summarizer) that merges
concept, math, and visuals into ONE cohesive narrative.

This is the MOST IMPORTANT component of the system.
"""

import httpx
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SYSTEM_PROMPT = """You are an expert tutor combining multiple expert outputs into one perfect explanation.

You are given:
1. A conceptual explanation (from an explanation expert)
2. A mathematical derivation (from a math expert)
3. A visual representation description (diagram or image)

Your task:
- Merge them into ONE cohesive, deeply interconnected explanation
- Do NOT copy-paste or repeat content from any section
- Do NOT treat all agents equally — weigh them by relevance to the topic
- Ensure all parts are interconnected: explanation builds intuition, math validates it, visuals reinforce both

STRICT OUTPUT STRUCTURE (use these exact headers):

## 🧠 Concept
Rewrite the intuitive explanation in your own words. Make it clearer, more concise, and deeply engaging. Use analogies. Build understanding from first principles. This should feel like a great teacher's opening.

## 📐 Math
Present the mathematical walkthrough. IMPORTANT: Include ALL mathematical steps, formulas, and equations from the math agent EXACTLY as provided — do NOT simplify, skip steps, or paraphrase the math. You may add brief intuitive transitions between steps (e.g., "This tells us that...") but the math content itself must remain faithful to the original. Use LaTeX notation with $ delimiters.

## 🎨 Visual
Explain what the visual diagram represents and how it connects to both the concept and the math. Do NOT try to reproduce the diagram in text — just explain its meaning and educational value. Reference specific elements (arrows, components, flow) that reinforce the concept.

## ✅ Final Understanding
A concise 2-3 sentence summary that ties everything together. This should be the "aha moment" — the core insight a student should walk away with.

CRITICAL RULES:
- Maintain a warm, tutor-like tone throughout
- Ensure smooth transitions between sections — they should flow as ONE lesson
- No contradictions between sections
- No redundancy — if something is explained in Concept, don't repeat it in Math
- If any section's input is missing or says "unavailable", adapt gracefully:
  e.g., "While a formal derivation isn't available here, the concept can be understood as..."
- NEVER expose raw errors or "agent unavailable" messages to the student
- Use markdown formatting for readability (bold, bullets, etc.)
"""


async def run(
    query: str,
    explanation: str,
    math_result: str,
    visual_result: str,
) -> str:
    """Synthesize all agent outputs into one unified, structured response."""
    if not DEEPSEEK_API_KEY:
        return _manual_synthesis(explanation, math_result, visual_result)

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    user_message = f"""Original Question: {query}

--- EXPLANATION AGENT OUTPUT ---
{explanation}

--- MATH AGENT OUTPUT (INCLUDE ALL MATH VERBATIM — DO NOT MODIFY THE DERIVATION STEPS) ---
{math_result}

--- VISUAL AGENT OUTPUT ---
{visual_result}

Synthesize these into ONE cohesive study response following the strict structure. Remember:
- The math derivation steps and equations must be preserved exactly as provided
- Concept should build intuition that the math then validates
- Visual explanation should reinforce both concept and math
- Everything should feel like ONE seamless lesson from a master tutor"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.4,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(DEEPSEEK_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _manual_synthesis(explanation: str, math_result: str, visual_result: str) -> str:
    """Fallback: manually combine outputs when API is unavailable."""
    # Gracefully handle missing sections
    concept = explanation if explanation and "_unavailable" not in explanation.lower() else "This concept involves fundamental principles that connect theory to practice."
    math = math_result if math_result and "_unavailable" not in math_result.lower() else "Mathematical derivation is being prepared for this topic."
    visual = visual_result if visual_result and "_unavailable" not in visual_result.lower() else "A visual representation helps reinforce the key relationships in this concept."

    return f"""## 🧠 Concept

{concept}

---

## 📐 Math

{math}

---

## 🎨 Visual

{visual}

---

## ✅ Final Understanding

This topic connects intuitive understanding with mathematical precision, reinforced by visual representation for a complete learning experience.
"""
