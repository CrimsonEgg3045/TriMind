"""
Database layer — Uses Supabase REST API for persistent chat history.
Replaces the previous SQLite implementation so data survives
Render free-tier server restarts.

Uses httpx (already a project dependency) to call the PostgREST API
directly, avoiding the heavy supabase Python SDK.
"""

import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# PostgREST endpoint
REST_URL = f"{SUPABASE_URL}/rest/v1" if SUPABASE_URL else ""

# Common headers for every request
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

_ready = bool(SUPABASE_URL and SUPABASE_KEY)

if _ready:
    print(f"[OK] Supabase REST client configured - {REST_URL}")
else:
    print("[WARN] SUPABASE_URL or SUPABASE_KEY not set. Chat history will not be saved.")


def save_chat(user_id: str, query: str, response: dict):
    """Saves a chat entry to Supabase. Enforces a max of 50 chats per user."""
    if not _ready:
        return

    try:
        response_json = json.dumps(response)

        # Insert the new chat
        httpx.post(
            f"{REST_URL}/chat_history",
            headers=HEADERS,
            json={
                "user_id": user_id,
                "query": query,
                "response": response_json,
            },
            timeout=10,
        ).raise_for_status()

        # Enforce limit of 50: fetch all IDs ordered by timestamp desc,
        # then delete anything beyond the 50th entry.
        resp = httpx.get(
            f"{REST_URL}/chat_history",
            headers=HEADERS,
            params={
                "select": "id",
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
            },
            timeout=10,
        )
        resp.raise_for_status()
        all_rows = resp.json()

        if len(all_rows) > 50:
            ids_to_delete = [row["id"] for row in all_rows[50:]]
            for old_id in ids_to_delete:
                httpx.delete(
                    f"{REST_URL}/chat_history",
                    headers=HEADERS,
                    params={"id": f"eq.{old_id}"},
                    timeout=10,
                ).raise_for_status()

    except Exception as e:
        print(f"[WARN] Error saving chat to Supabase: {e}")


def get_history(user_id: str, limit: int = 50):
    """Retrieves the chat history for a user from Supabase."""
    if not _ready:
        return []

    try:
        resp = httpx.get(
            f"{REST_URL}/chat_history",
            headers=HEADERS,
            params={
                "select": "query,response,created_at",
                "user_id": f"eq.{user_id}",
                "order": "created_at.asc",
                "limit": str(limit),
            },
            timeout=10,
        )
        resp.raise_for_status()

        history = []
        for row in resp.json():
            history.append({
                "query": row["query"],
                "response": json.loads(row["response"]),
                "timestamp": row["created_at"],
            })

        return history

    except Exception as e:
        print(f"[WARN] Error fetching history from Supabase: {e}")
        return []
