"""
Check Gemini API — Quick diagnostic to verify the Gemini API key works.
"""

import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


async def main():
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set in .env")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        models = r.json().get("models", [])
        print(f"Total models available: {len(models)}\n")
        for m in sorted(models, key=lambda x: x.get("name", "")):
            name = m.get("name", "?")
            display = m.get("displayName", "?")
            print(f"  {name}  ({display})")


asyncio.run(main())
