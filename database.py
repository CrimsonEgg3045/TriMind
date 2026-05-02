import sqlite3
import json
import os
from datetime import datetime

DB_FILE = "history.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create an index on user_id and timestamp for faster fetching
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_timestamp ON chat_history (user_id, timestamp DESC)
    ''')
    conn.commit()
    conn.close()

def save_chat(user_id: str, query: str, response: dict):
    """Saves a chat and ensures the user only has max 50 chats kept."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Store response as JSON string
    response_json = json.dumps(response)
    
    cursor.execute('''
        INSERT INTO chat_history (user_id, query, response)
        VALUES (?, ?, ?)
    ''', (user_id, query, response_json))
    
    # Enforce limit of 50
    cursor.execute('''
        DELETE FROM chat_history
        WHERE id IN (
            SELECT id FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT -1 OFFSET 50
        )
    ''', (user_id,))
    
    conn.commit()
    conn.close()

def get_history(user_id: str, limit: int = 50):
    """Retrieves the history for a user, up to `limit` items."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT query, response, timestamp FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
    ''', (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "query": row["query"],
            "response": json.loads(row["response"]),
            "timestamp": row["timestamp"]
        })
        
    return history

# Initialize DB on import
init_db()
