"""
Tri Mind — Multi-Agent AI Study Assistant — FastAPI Backend
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import orchestrator

app = FastAPI(title="Tri Mind — AI Study Assistant", version="1.0.0")

FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


class AskRequest(BaseModel):
    query: str
    use_demo: bool = True


@app.post("/api/ask")
async def ask(request: AskRequest):
    try:
        result = await orchestrator.process_query(
            query=request.query,
            use_demo=request.use_demo,
        )
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "An error occurred. Please try again."},
        )


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "agents": {
            "explanation": bool(os.getenv("GROQ_API_KEY")),
            "math": bool(os.getenv("OPENROUTER_API_KEY")),
            "visual": True,  # Pollinations.ai — free, no key needed
            "synthesizer": bool(os.getenv("GROQ_API_KEY")),
        },
    }
