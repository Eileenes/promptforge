"""Prompt CRUD router for PromptForge."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db, now_iso
from services.optimizer import optimizer

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


class PromptCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    description: str = ""
    tags: list[str] = []


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None


@router.post("")
async def create_prompt(prompt: PromptCreate):
    db = await get_db()
    try:
        token_count = optimizer.count_tokens(prompt.content)
        tags_str = str(prompt.tags) if prompt.tags else "[]"
        now = now_iso()
        cursor = await db.execute(
            """INSERT INTO prompts (title, category, content, description, tags, version, token_count, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)""",
            (prompt.title, prompt.category, prompt.content, prompt.description, tags_str, token_count, now, now),
        )
        await db.commit()
        return {"id": cursor.lastrowid, "message": "Prompt created", "token_count": token_count}
    finally:
        await db.close()


@router.get("")
async def list_prompts(category: str = None, search: str = None):
    db = await get_db()
    try:
        query = "SELECT * FROM prompts"
        params = []
        conditions = []
        if category:
            conditions.append("category = ?")
            params.append(category)
        if search:
            conditions.append("(title LIKE ? OR content LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY updated_at DESC"
        rows = await db.execute(query, params)
        results = [dict(row) for row in await rows.fetchall()]
        for r in results:
            r["tags"] = eval(r["tags"]) if r["tags"] else []
        return results
    finally:
        await db.close()


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: int):
    db = await get_db()
    try:
        row = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Prompt not found")
        result = dict(row)
        result["tags"] = eval(result["tags"]) if result["tags"] else []
        return result
    finally:
        await db.close()


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: int, prompt: PromptUpdate):
    db = await get_db()
    try:
        existing = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Prompt not found")

        updates = {}
        if prompt.title is not None:
            updates["title"] = prompt.title
        if prompt.content is not None:
            updates["content"] = prompt.content
            updates["token_count"] = optimizer.count_tokens(prompt.content)
        if prompt.category is not None:
            updates["category"] = prompt.category
        if prompt.description is not None:
            updates["description"] = prompt.description
        if prompt.tags is not None:
            updates["tags"] = str(prompt.tags)

        # Increment version when content changes
        if prompt.content is not None:
            updates["version"] = existing["version"] + 1

        updates["updated_at"] = now_iso()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [prompt_id]
        await db.execute(f"UPDATE prompts SET {set_clause} WHERE id = ?", values)
        await db.commit()
        return {"message": "Prompt updated", "version": updates.get("version", existing["version"])}
    finally:
        await db.close()


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: int):
    db = await get_db()
    try:
        await db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        await db.execute("DELETE FROM test_runs WHERE prompt_id = ?", (prompt_id,))
        await db.execute("DELETE FROM optimizations WHERE original_prompt_id = ?", (prompt_id,))
        await db.commit()
        return {"message": "Prompt deleted"}
    finally:
        await db.close()


@router.get("/{prompt_id}/versions")
async def get_versions(prompt_id: int):
    """Get version history of a prompt."""
    db = await get_db()
    try:
        # Get the prompt and its parent chain
        row = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Find all prompts in the version chain
        versions = []
        current_id = row["parent_id"] if row["parent_id"] else prompt_id
        if row["parent_id"]:
            # This is a child - find the root and all descendants
            root_id = row["parent_id"]
            all_rows = await (await db.execute(
                "SELECT * FROM prompts WHERE id = ? OR parent_id = ? ORDER BY version ASC",
                (root_id, root_id)
            )).fetchall()
            versions = [dict(r) for r in all_rows]
        else:
            # This is a root - find all children
            all_rows = await (await db.execute(
                "SELECT * FROM prompts WHERE id = ? OR parent_id = ? ORDER BY version ASC",
                (prompt_id, prompt_id)
            )).fetchall()
            versions = [dict(r) for r in all_rows]

        for v in versions:
            v["tags"] = eval(v["tags"]) if v["tags"] else []
        return versions
    finally:
        await db.close()
