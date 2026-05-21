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
from typing import Optional
from pydantic import BaseModel
import orchestrator
from google.oauth2 import id_token
from google.auth.transport import requests
import database

app = FastAPI(title="Tri Mind — AI Study Assistant", version="2.0.0")

FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


class AskRequest(BaseModel):
    query: str
    use_demo: bool = True
    user_id: Optional[str] = None
    incognito: bool = False

class VerifyRequest(BaseModel):
    credential: str

@app.post("/api/auth/verify")
async def verify_auth(request: VerifyRequest):
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not client_id:
            # For ease of testing, if no client ID is set, we return a mock user or error.
            # Let's return error so they know to set it.
            return JSONResponse(status_code=400, content={"status": "error", "message": "GOOGLE_CLIENT_ID not set in backend."})
            
        idinfo = id_token.verify_oauth2_token(request.credential, requests.Request(), client_id)
        userid = idinfo['sub']
        return {
            "status": "success", 
            "user": {
                "id": userid, 
                "name": idinfo.get("name"), 
                "email": idinfo.get("email"), 
                "picture": idinfo.get("picture")
            }
        }
    except ValueError as e:
        return JSONResponse(status_code=401, content={"status": "error", "message": str(e)})

@app.get("/api/history")
async def get_history(user_id: str):
    try:
        history = database.get_history(user_id)
        return {"status": "success", "history": history}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/ask")
async def ask(request: AskRequest):
    try:
        result = await orchestrator.process_query(
            query=request.query,
            use_demo=request.use_demo,
        )
        
        # Save to history if logged in and not incognito
        if request.user_id and not request.incognito:
            database.save_chat(request.user_id, request.query, result)
            
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
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "agents": {
            "explanation": bool(os.getenv("DEEPSEEK_API_KEY")),
            "math": bool(os.getenv("OPENROUTER_API_KEY")),
            "visual": bool(os.getenv("DEEPSEEK_API_KEY")),
            "synthesizer": bool(os.getenv("DEEPSEEK_API_KEY")),
        },
    }
