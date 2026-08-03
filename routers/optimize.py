"""Prompt optimization router for PromptForge."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db, now_iso
from services.optimizer import optimizer

router = APIRouter(prefix="/api/optimize", tags=["optimize"])


class OptimizeRequest(BaseModel):
    content: str
    strategy: str = "balanced"  # minimal, balanced, aggressive
    prompt_id: int = None


@router.post("")
async def optimize_prompt(req: OptimizeRequest):
    """Optimize a prompt to reduce token usage."""
    if req.strategy not in ("minimal", "balanced", "aggressive"):
        raise HTTPException(status_code=400, detail="Strategy must be: minimal, balanced, or aggressive")

    result = optimizer.optimize(req.content, req.strategy)

    # Save optimization record if prompt_id is provided
    if req.prompt_id:
        db = await get_db()
        try:
            await db.execute(
                """INSERT INTO optimizations
                   (original_prompt_id, optimized_content, strategy, original_tokens, optimized_tokens, reduction_pct, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (req.prompt_id, result["optimized_content"], req.strategy,
                 result["original_tokens"], result["optimized_tokens"],
                 result["reduction_pct"], now_iso()),
            )
            await db.commit()
        finally:
            await db.close()

    return result


@router.post("/save")
async def save_optimized_prompt(req: OptimizeRequest):
    """Optimize a prompt and save the optimized version as a new version."""
    if not req.prompt_id:
        raise HTTPException(status_code=400, detail="prompt_id is required to save")

    result = optimizer.optimize(req.content, req.strategy)

    db = await get_db()
    try:
        # Get original prompt
        original = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (req.prompt_id,))).fetchone()
        if not original:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Create new version
        now = now_iso()
        cursor = await db.execute(
            """INSERT INTO prompts (title, category, content, description, tags, version, parent_id, token_count, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (original["title"], original["category"], result["optimized_content"],
             original["description"], original["tags"], original["version"] + 1,
             original["id"], result["optimized_tokens"], now, now),
        )
        await db.execute(
            """INSERT INTO optimizations
               (original_prompt_id, optimized_content, strategy, original_tokens, optimized_tokens, reduction_pct, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (req.prompt_id, result["optimized_content"], req.strategy,
             result["original_tokens"], result["optimized_tokens"],
             result["reduction_pct"], now),
        )
        await db.commit()
        return {
            "new_prompt_id": cursor.lastrowid,
            "message": "Optimized prompt saved as new version",
            **result,
        }
    finally:
        await db.close()
