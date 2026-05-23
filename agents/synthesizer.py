"""
Final Synthesis Agent — Powered by DeepSeek API
Acts as an INTELLIGENT ORCHESTRATOR (not a summarizer) that merges
concept, math, and visuals into ONE cohesive narrative.

Supports user-requested section exclusions — when a section is excluded,
the synthesizer omits it entirely from the output structure.

This is the MOST IMPORTANT component of the system.
"""

import httpx
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

# ── Base system prompt (always included) ────────────────────────────

_BASE_SYSTEM_PROMPT = """\
You are an expert tutor combining multiple expert outputs into one perfect explanation.

Your task:
- Merge the provided expert outputs into ONE cohesive, deeply interconnected explanation
- Do NOT copy-paste or repeat content from any section
- Do NOT treat all agents equally — weigh them by relevance to the topic
- Ensure all parts are interconnected and flow naturally

{section_instructions}

CRITICAL RULES:
- Maintain a warm, tutor-like tone throughout
- Ensure smooth transitions between sections — they should flow as ONE lesson
- No contradictions between sections
- No redundancy — if something is explained in one section, don't repeat it in another
- If any section's input is missing or says "unavailable", adapt gracefully:
  e.g., "While a formal derivation isn't available here, the concept can be understood as..."
- NEVER expose raw errors or "agent unavailable" messages to the student
- Use markdown formatting for readability (bold, bullets, etc.)
"""

# ── Per-section instruction blocks ──────────────────────────────────

_SECTION_CONCEPT = """\
## 🧠 Concept
Rewrite the intuitive explanation in your own words. Make it clearer, more concise, and deeply engaging. Use analogies. Build understanding from first principles. This should feel like a great teacher's opening."""

_SECTION_MATH = """\
## 📐 Math
Present the mathematical walkthrough. IMPORTANT: Include ALL mathematical steps, formulas, and equations from the math agent EXACTLY as provided — do NOT simplify, skip steps, or paraphrase the math. You may add brief intuitive transitions between steps (e.g., "This tells us that...") but the math content itself must remain faithful to the original. Use LaTeX notation with $ delimiters."""

_SECTION_VISUAL = """\
## 🎨 Visual
Explain what the visual diagram represents and how it connects to both the concept and the math. Do NOT try to reproduce the diagram in text — just explain its meaning and educational value. Reference specific elements (arrows, components, flow) that reinforce the concept."""

_SECTION_FINAL = """\
## ✅ Final Understanding
A concise 2-3 sentence summary that ties everything together. This should be the "aha moment" — the core insight a student should walk away with."""


def _build_system_prompt(excluded: set[str]) -> str:
    """Build the system prompt dynamically, omitting excluded sections."""
    sections = []

    sections.append("STRICT OUTPUT STRUCTURE (use ONLY these exact headers):\n")

    if "explanation" not in excluded:
        sections.append(_SECTION_CONCEPT)
    if "math" not in excluded:
        sections.append(_SECTION_MATH)
    if "visual" not in excluded:
        sections.append(_SECTION_VISUAL)

    # Final Understanding is always included
    sections.append(_SECTION_FINAL)

    # Add exclusion notice so the model knows NOT to generate those sections
    if excluded:
        excluded_labels = {
            "explanation": "Concept (🧠 Concept)",
            "math": "Math (📐 Math)",
            "visual": "Visual (🎨 Visual)",
        }
        excluded_names = [excluded_labels[s] for s in excluded if s in excluded_labels]
        sections.append(
            f"\nIMPORTANT: The user has explicitly requested that the following sections "
            f"be EXCLUDED from the response: {', '.join(excluded_names)}. "
            f"Do NOT include those section headers or any content for them. "
            f"Only output the sections listed above."
        )

    return _BASE_SYSTEM_PROMPT.format(section_instructions="\n\n".join(sections))


def _build_user_message(
    query: str,
    explanation: str | None,
    math_result: str | None,
    visual_result: str | None,
    excluded: set[str],
) -> str:
    """Build the user message, including only non-excluded agent outputs."""
    parts = [f"Original Question: {query}\n"]

    if "explanation" not in excluded and explanation is not None:
        parts.append(f"--- EXPLANATION AGENT OUTPUT ---\n{explanation}\n")

    if "math" not in excluded and math_result is not None:
        parts.append(
            f"--- MATH AGENT OUTPUT (INCLUDE ALL MATH VERBATIM — DO NOT MODIFY THE DERIVATION STEPS) ---\n{math_result}\n"
        )

    if "visual" not in excluded and visual_result is not None:
        parts.append(f"--- VISUAL AGENT OUTPUT ---\n{visual_result}\n")

    # Synthesis instructions
    active_parts = []
    if "explanation" not in excluded:
        active_parts.append("Concept should build intuition")
    if "math" not in excluded:
        active_parts.append("Math derivation steps and equations must be preserved exactly as provided")
    if "visual" not in excluded:
        active_parts.append("Visual explanation should reinforce the concept")

    parts.append(
        "Synthesize these into ONE cohesive study response following the strict structure. Remember:\n"
        + "\n".join(f"- {p}" for p in active_parts)
        + "\n- Everything should feel like ONE seamless lesson from a master tutor"
    )

    return "\n".join(parts)


async def run(
    query: str,
    explanation: str | None,
    math_result: str | None,
    visual_result: str | None,
    excluded_sections: set[str] | None = None,
) -> str:
    """Synthesize all agent outputs into one unified, structured response."""
    excluded = excluded_sections or set()

    if not DEEPSEEK_API_KEY:
        return _manual_synthesis(explanation, math_result, visual_result, excluded)

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = _build_system_prompt(excluded)
    user_message = _build_user_message(query, explanation, math_result, visual_result, excluded)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
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


def _manual_synthesis(
    explanation: str | None,
    math_result: str | None,
    visual_result: str | None,
    excluded: set[str] | None = None,
) -> str:
    """Fallback: manually combine outputs when API is unavailable."""
    excluded = excluded or set()

    parts = []

    if "explanation" not in excluded:
        concept = (
            explanation
            if explanation and "_unavailable" not in explanation.lower()
            else "This concept involves fundamental principles that connect theory to practice."
        )
        parts.append(f"## 🧠 Concept\n\n{concept}")

    if "math" not in excluded:
        math_text = (
            math_result
            if math_result and "_unavailable" not in math_result.lower()
            else "Mathematical derivation is being prepared for this topic."
        )
        parts.append(f"## 📐 Math\n\n{math_text}")

    if "visual" not in excluded:
        vis = (
            visual_result
            if visual_result and "_unavailable" not in visual_result.lower()
            else "A visual representation helps reinforce the key relationships in this concept."
        )
        parts.append(f"## 🎨 Visual\n\n{vis}")

    parts.append(
        "## ✅ Final Understanding\n\n"
        "This topic connects intuitive understanding with mathematical precision, "
        "reinforced by visual representation for a complete learning experience."
    )

    return "\n\n---\n\n".join(parts) + "\n"
