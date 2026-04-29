import httpx, asyncio
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_api_key_here")

async def main():
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        )
        models = r.json()["data"]
        free = [m for m in models if ":free" in m["id"]]
        print(f"Total free models: {len(free)}\n")
        for m in sorted(free, key=lambda x: x["id"]):
            ctx = m.get("context_length", "?")
            print(f"  {m['id']}  (ctx={ctx})")

asyncio.run(main())
