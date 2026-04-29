"""
Orchestrator — Coordinates all agents in parallel using asyncio.
Handles fault tolerance, timeouts, and demo mode caching.
"""

import asyncio
from agents import explanation, math, visual, synthesizer
from demo_cache import get_cached_response


async def process_query(query: str, use_demo: bool = True) -> dict:
    """
    Process a user query through all agents and synthesize the result.
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

    # --- Run all agents in parallel with fault tolerance ---
    explanation_result, math_result, visual_result = await asyncio.gather(
        _safe_call("explanation", explanation.run(query)),
        _safe_call("math", math.run(query)),
        _safe_call("visual", visual.run(query)),
        return_exceptions=False,
    )

    # Extract visual text and optional image
    if isinstance(visual_result, dict):
        visual_text = visual_result.get("text", "_Visual section unavailable._")
        visual_image = visual_result.get("image", None)
    else:
        visual_text = str(visual_result)
        visual_image = None

    # --- Run synthesizer ---
    try:
        synthesized = await asyncio.wait_for(
            synthesizer.run(
                query=query,
                explanation=explanation_result,
                math_result=math_result,
                visual_result=visual_text,
            ),
            timeout=50.0,
        )
    except Exception as e:
        synthesized = synthesizer._manual_synthesis(
            explanation_result, math_result, visual_text
        )

    return {
        "source": "live",
        "query": query,
        "synthesized": synthesized,
        "visual_image": visual_image,
    }


async def _safe_call(agent_name: str, coro):
    """Wrap an agent call with timeout and error handling."""
    try:
        return await asyncio.wait_for(coro, timeout=60.0)
    except asyncio.TimeoutError:
        return f"_⏱️ The {agent_name} agent timed out. This section is temporarily unavailable._"
    except Exception as e:
        return f"_⚠️ The {agent_name} agent encountered an error: {str(e)[:100]}. This section is temporarily unavailable._"
