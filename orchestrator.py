"""
Orchestrator — Coordinates all agents in parallel using asyncio.
Handles fault tolerance, timeouts, and demo mode caching.
Supports diagram objects (SVG/Canvas/Chart.js) and fallback images.
Supports user-requested section exclusions (math, visual, explanation).
"""

import asyncio
import re
from agents import explanation, math, visual, synthesizer
from demo_cache import get_cached_response


# ── Exclusion detection ─────────────────────────────────────────────
# Only triggers on EXPLICIT user phrases — never inferred by agents.

_EXCLUSION_PATTERNS = {
    "explanation": re.compile(
        "(?:do\\s*n[o']?t|don[\u2019\u2018']t|no|skip|remove|exclude|without|hide|omit|leave\\s+out|don't)"
        "\\s+(?:give\\s+)?(?:the\\s+|any\\s+)?"
        "(?:concept(?:ual)?\\s+)?(?:explanation)",
        re.IGNORECASE,
    ),
    "math": re.compile(
        "(?:do\\s*n[o']?t|don[\u2019\u2018']t|no|skip|remove|exclude|without|hide|omit|leave\\s+out|don't)"
        "\\s+(?:give\\s+)?(?:the\\s+|any\\s+)?"
        "(?:math(?:ematic(?:al)?|s)?|derivation|formula|equation)"
        "(?:\\s+(?:explanation|section|part|derivation))?",
        re.IGNORECASE,
    ),
    "visual": re.compile(
        "(?:do\\s*n[o']?t|don[\u2019\u2018']t|no|skip|remove|exclude|without|hide|omit|leave\\s+out|don't)"
        "\\s+(?:give\\s+)?(?:the\\s+|any\\s+)?"
        "(?:visual(?:i[sz]ation|s)?|diagram|image|picture|visual\\s+aid)",
        re.IGNORECASE,
    ),
}


def _detect_exclusions(query: str) -> set[str]:
    """
    Scan the user query for explicit exclusion requests.
    Returns a set of section names to exclude: {'explanation', 'math', 'visual'}.
    """
    excluded = set()
    for section, pattern in _EXCLUSION_PATTERNS.items():
        if pattern.search(query):
            excluded.add(section)
    return excluded


# ── Main orchestration ──────────────────────────────────────────────


async def process_query(query: str, use_demo: bool = True) -> dict:
    """
    Process a user query through all agents and synthesize the result.
    Respects explicit user exclusion requests.
    """

    # --- Demo Mode: Check cache first ---
    if use_demo:
        cached = get_cached_response(query)
        if cached:
            return {
                "source": "demo_cache",
                "query": query,
                **cached,
            }

    # --- Detect which sections the user explicitly wants excluded ---
    excluded = _detect_exclusions(query)

    # --- Build agent tasks (skip excluded agents) ---
    tasks = {}
    if "explanation" not in excluded:
        tasks["explanation"] = _safe_call("explanation", explanation.run(query))
    if "math" not in excluded:
        tasks["math"] = _safe_call("math", math.run(query))
    if "visual" not in excluded:
        tasks["visual"] = _safe_call("visual", visual.run(query))

    # Run all non-excluded agents in parallel
    if tasks:
        results = await asyncio.gather(*tasks.values(), return_exceptions=False)
        agent_results = dict(zip(tasks.keys(), results))
    else:
        agent_results = {}

    # Use None for excluded sections so synthesizer knows what was skipped
    explanation_result = agent_results.get("explanation")
    math_result = agent_results.get("math")
    visual_raw = agent_results.get("visual")

    # Extract visual components (diagram, image, text)
    visual_text = ""
    visual_diagram = None
    visual_image = None

    if "visual" not in excluded and visual_raw is not None:
        if isinstance(visual_raw, dict):
            visual_text = visual_raw.get("text", "")
            visual_type = visual_raw.get("type", "text")

            if visual_type == "diagram" and visual_raw.get("diagram"):
                visual_diagram = visual_raw["diagram"]
            elif visual_type == "image" and visual_raw.get("image"):
                visual_image = visual_raw["image"]
        else:
            visual_text = str(visual_raw)

    # --- Run synthesizer (ALWAYS called) ---
    try:
        synthesized = await asyncio.wait_for(
            synthesizer.run(
                query=query,
                explanation=explanation_result,
                math_result=math_result,
                visual_result=visual_text if "visual" not in excluded else None,
                excluded_sections=excluded,
            ),
            timeout=60.0,
        )
    except Exception:
        synthesized = synthesizer._manual_synthesis(
            explanation_result, math_result, visual_text, excluded,
        )

    return {
        "source": "live",
        "query": query,
        "synthesized": synthesized,
        "visual_diagram": visual_diagram if "visual" not in excluded else None,
        "visual_image": visual_image if "visual" not in excluded else None,
    }


async def _safe_call(agent_name: str, coro):
    """Wrap an agent call with timeout and error handling."""
    try:
        return await asyncio.wait_for(coro, timeout=60.0)
    except asyncio.TimeoutError:
        return f"_The {agent_name} section is being prepared and will be available shortly._"
    except Exception as e:
        return f"_The {agent_name} section is temporarily being updated._"
