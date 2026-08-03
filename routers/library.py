"""Prompt template library router for PromptForge."""
import json
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db, now_iso
from services.optimizer import optimizer

router = APIRouter(prefix="/api/library", tags=["library"])

LIBRARY_PATH = Path(__file__).parent.parent / "data" / "prompt_library.json"


class ImportTemplateRequest(BaseModel):
    template_id: str


@router.get("")
async def get_library():
    """Get the curated prompt template library."""
    if LIBRARY_PATH.exists():
        with open(LIBRARY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": []}


@router.post("/import")
async def import_template(req: ImportTemplateRequest):
    """Import a template from the library into the user's prompts."""
    if not LIBRARY_PATH.exists():
        return {"error": "Library not found"}

    with open(LIBRARY_PATH, "r", encoding="utf-8") as f:
        library = json.load(f)

    template = None
    for category in library.get("categories", []):
        for t in category.get("prompts", []):
            if t["id"] == req.template_id:
                template = t
                break
        if template:
            break

    if not template:
        return {"error": "Template not found"}

    db = await get_db()
    try:
        token_count = optimizer.count_tokens(template["content"])
        now = now_iso()
        cursor = await db.execute(
            """INSERT INTO prompts (title, category, content, description, tags, version, token_count, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)""",
            (template["title"], template.get("category", "general"),
             template["content"], template.get("description", ""),
             str(template.get("tags", [])), token_count, now, now),
        )
        await db.commit()
        return {"id": cursor.lastrowid, "message": "Template imported"}
    finally:
        await db.close()


@router.get("/search")
async def search_templates(q: str = ""):
    """Search templates in the library."""
    if not LIBRARY_PATH.exists():
        return []

    with open(LIBRARY_PATH, "r", encoding="utf-8") as f:
        library = json.load(f)

    results = []
    query = q.lower()
    for category in library.get("categories", []):
        for t in category.get("prompts", []):
            if not query or query in t["title"].lower() or query in t.get("description", "").lower():
                results.append({
                    **t,
                    "category": category["name"],
                })
    return results
