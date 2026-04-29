"""
Visual Agent — Powered by Pollinations.ai (Free, no API key needed)
Always attempts image generation.
Falls back to text-based visual description if image generation fails.
"""

import httpx
import base64
import asyncio
from urllib.parse import quote

# Pollinations.ai — completely free, no API key required
POLLINATIONS_URL = "https://image.pollinations.ai/prompt"


async def _generate_image(query: str) -> dict | None:
    """Generate an image using Pollinations.ai. Returns base64 data or None."""

    prompt = (
        f"Educational diagram explaining {query}, "
        "clean scientific illustration, labeled, white background, "
        "high quality, detailed, professional"
    )
    encoded_prompt = quote(prompt)
    image_url = f"{POLLINATIONS_URL}/{encoded_prompt}?width=1024&height=576&nologo=true&seed=42"

    try:
        async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
            response = await client.get(image_url)

            if response.status_code == 200 and "image" in response.headers.get(
                "content-type", ""
            ):
                img_base64 = base64.b64encode(response.content).decode("utf-8")
                content_type = response.headers.get("content-type", "image/jpeg")
                return {
                    "type": "image",
                    "data": f"data:{content_type};base64,{img_base64}",
                }
            return None
    except Exception:
        return None


def _offline_visual_fallback(query: str) -> str:
    """Generate a basic structured visual explanation without any API."""
    return f"""### Visual Representation: {query}

**Conceptual Diagram:**

```
+-------------------------------------------+
|              {query[:30]:<30s}   |
+-------------------------------------------+
|                                           |
|   +-----------+     +-----------+         |
|   |  Input /  |---->|  Core     |         |
|   |  Premise  |     |  Process  |         |
|   +-----------+     +-----+-----+         |
|                           |               |
|                           v               |
|                     +-----------+         |
|                     |  Output / |         |
|                     |  Result   |         |
|                     +-----------+         |
|                                           |
+-------------------------------------------+
```

**Key Visual Elements:**
- **Input Layer**: The starting conditions, variables, or assumptions
- **Processing Core**: The main transformation, operation, or mechanism
- **Output Layer**: The resulting behavior, value, or conclusion
"""


async def run(query: str) -> dict:
    """
    Run the visual agent. ALWAYS attempts image generation via Pollinations.ai.
    Returns a dict with 'text' (always) and optionally 'image' (base64).
    """
    # Generate text description (offline fallback)
    text_result = _offline_visual_fallback(query)

    # Attempt image generation
    try:
        image_result = await _generate_image(query)
    except Exception:
        image_result = None

    return {"text": text_result, "image": image_result}
