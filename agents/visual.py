"""
Visual Agent — Powered by DeepSeek API (Primary) + Cloudflare Workers AI (Fallback)

PRIMARY MODE (default): Uses DeepSeek to generate structured diagram code
  → Outputs renderable SVG / Canvas / Chart.js code

SECONDARY MODE (fallback): Uses Cloudflare Workers AI for abstract concepts
  → Generates clean educational images when diagrams aren't feasible

Modes are MUTUALLY EXCLUSIVE — diagram XOR image, never both.
"""

import httpx
import base64
import json
import os
import re

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Cloudflare Worker endpoint for fallback image generation
WORKER_URL = os.getenv(
    "CF_WORKER_URL", "https://ai-image-worker.imadbahadur16.workers.dev"
)
GENERATE_ENDPOINT = f"{WORKER_URL}/generate"

# ── DeepSeek Diagram Generation Prompt ──────────────────────────────

DIAGRAM_SYSTEM_PROMPT = """You are an expert educational diagram generator. Your job is to create clean, structured visual diagrams using code that can be rendered in a web browser.

You MUST respond with ONLY a valid JSON object (no markdown fencing, no extra text). The JSON must follow this exact schema:

{
  "type": "diagram",
  "format": "svg",
  "code": "<complete SVG code as a string>",
  "description": "<one-sentence description of what this diagram shows>",
  "feasible": true
}

DIAGRAM RULES:
- Use ONLY: lines, arrows, circles, rectangles, and text labels
- Ensure clean, logical layout with proper spacing
- Use educational clarity — the diagram should teach, not just decorate
- Use colors sparingly: primarily black (#1a1a2e) and blue (#3b82f6) with white (#ffffff) background
- All text must be legible (minimum 12px font size)
- The SVG should have a viewBox and be responsive (no fixed width/height in px on the root element)
- Include proper arrow markers using <defs> and <marker> elements
- The diagram MUST directly correspond to the concept being explained

SVG SPECIFIC RULES:
- Always set viewBox attribute (e.g., viewBox="0 0 600 400")
- Set width="100%" on the root <svg> element
- Use readable font: font-family="Inter, Arial, sans-serif"
- Add a subtle background rectangle with fill="#ffffff" and rounded corners

If a diagrammatic representation is NOT feasible for this concept (e.g., it's too abstract like entropy, consciousness, quantum states), respond with:
{
  "type": "diagram",
  "format": "svg",
  "code": "",
  "description": "",
  "feasible": false
}
"""

# ── Strict Cloudflare Image Prompt Template ─────────────────────────

STRICT_IMAGE_PROMPT = (
    "Create a SIMPLE, CLEAN educational diagram of: {topic}. "
    "STRICT RULES: White background. Minimal elements only. "
    "NO artistic effects. NO complex layouts. NO decorative visuals. "
    "Only basic shapes (lines, arrows, circles). Clear labeled components. "
    "No paragraphs of text. No fake text. "
    "Style: textbook diagram, black and blue lines only, simple and clean."
)


async def _generate_diagram(query: str) -> dict | None:
    """Use DeepSeek to generate structured diagram code (SVG/Canvas/Chart.js)."""
    if not DEEPSEEK_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": DIAGRAM_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Generate a clean, educational SVG diagram for: {query}",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 3000,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(DEEPSEEK_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Strip markdown code fences if present
            content = content.strip()
            if content.startswith("```"):
                # Remove opening fence (```json or ```)
                content = re.sub(r"^```\w*\n?", "", content)
                # Remove closing fence
                content = re.sub(r"\n?```$", "", content)
                content = content.strip()

            diagram_data = json.loads(content)

            # Check if diagram is feasible
            if not diagram_data.get("feasible", True):
                return None

            # Validate required fields
            if diagram_data.get("code") and diagram_data.get("format"):
                return {
                    "format": diagram_data["format"],
                    "code": diagram_data["code"],
                    "description": diagram_data.get("description", ""),
                }
            return None
    except (json.JSONDecodeError, KeyError, httpx.HTTPError):
        return None


async def _generate_fallback_image(query: str) -> dict | None:
    """Generate an image using Cloudflare Workers AI as fallback."""
    prompt = STRICT_IMAGE_PROMPT.format(topic=query)
    payload = {"prompt": prompt}

    try:
        async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
            response = await client.post(
                GENERATE_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")

            if "image" in content_type:
                img_base64 = base64.b64encode(response.content).decode("utf-8")
                return {
                    "type": "image",
                    "data": f"data:{content_type};base64,{img_base64}",
                }
            return None
    except Exception:
        return None


async def run(query: str) -> dict:
    """
    Run the visual agent.

    PRIMARY: Attempts DeepSeek-powered SVG diagram generation.
    FALLBACK: If diagram is not feasible, falls back to Cloudflare image generation.

    Modes are mutually exclusive — returns diagram OR image, never both.
    """

    # ── PRIMARY: Try diagram generation via DeepSeek ──
    diagram_result = None
    try:
        diagram_result = await _generate_diagram(query)
    except Exception:
        diagram_result = None

    if diagram_result:
        return {
            "type": "diagram",
            "diagram": diagram_result,
            "image": None,
            "text": f"**Diagram:** {diagram_result.get('description', 'Visual representation of ' + query)}",
        }

    # ── FALLBACK: Generate image via Cloudflare Workers AI ──
    image_result = None
    try:
        image_result = await _generate_fallback_image(query)
    except Exception:
        image_result = None

    if image_result:
        return {
            "type": "image",
            "diagram": None,
            "image": image_result,
            "text": f"**Visual:** Educational diagram of {query}",
        }

    # ── LAST RESORT: Text-only description ──
    return {
        "type": "text",
        "diagram": None,
        "image": None,
        "text": f"**Visual Representation of {query}:** A visual diagram would typically illustrate the key components and relationships in this concept.",
    }
