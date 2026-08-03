"""SQLite database layer for PromptForge."""
import aiosqlite
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "promptforge.db"


async def init_db():
    """Initialize the database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                content TEXT NOT NULL,
                description TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                version INTEGER DEFAULT 1,
                parent_id INTEGER,
                token_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                input_text TEXT DEFAULT '',
                output_text TEXT DEFAULT '',
                latency_ms INTEGER DEFAULT 0,
                token_input INTEGER DEFAULT 0,
                token_output INTEGER DEFAULT 0,
                score REAL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (prompt_id) REFERENCES prompts(id)
            );

            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_prompt_id INTEGER NOT NULL,
                optimized_content TEXT NOT NULL,
                strategy TEXT DEFAULT 'balanced',
                original_tokens INTEGER DEFAULT 0,
                optimized_tokens INTEGER DEFAULT 0,
                reduction_pct REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (original_prompt_id) REFERENCES prompts(id)
            );
        """)
        await db.commit()


async def get_db():
    """Get a database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


def now_iso():
    return datetime.now().isoformat()
