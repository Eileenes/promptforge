"""Prompt testing and benchmarking router for PromptForge."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db, now_iso
from services.llm_provider import llm_provider
from services.benchmark import benchmark

router = APIRouter(prefix="/api/test", tags=["test"])


class TestRequest(BaseModel):
    prompt_id: int
    provider: str = "mock"
    model: str = "mock-standard"
    input_text: str = ""


class BenchmarkRequest(BaseModel):
    content: str
    prompt_id: int = None


@router.get("/providers")
async def list_providers():
    """List available LLM providers and models."""
    return llm_provider.list_providers()


@router.post("/run")
async def run_test(req: TestRequest):
    """Run a prompt against an LLM provider and record results."""
    db = await get_db()
    try:
        # Get the prompt
        prompt = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (req.prompt_id,))).fetchone()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Call the LLM
        result = await llm_provider.call(req.provider, req.model, prompt["content"], req.input_text)

        # Save test run
        now = now_iso()
        cursor = await db.execute(
            """INSERT INTO test_runs
               (prompt_id, provider, model, input_text, output_text, latency_ms,
                token_input, token_output, score, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (req.prompt_id, req.provider, req.model, req.input_text, result["output"],
             result["latency_ms"], result["tokens_input"], result["tokens_output"],
             0, "", now),
        )
        await db.commit()

        return {
            "test_id": cursor.lastrowid,
            "provider": req.provider,
            "model": req.model,
            "output": result["output"],
            "latency_ms": result["latency_ms"],
            "tokens_input": result["tokens_input"],
            "tokens_output": result["tokens_output"],
        }
    finally:
        await db.close()


@router.get("/runs/{prompt_id}")
async def get_test_runs(prompt_id: int):
    """Get all test runs for a prompt."""
    db = await get_db()
    try:
        rows = await (await db.execute(
            "SELECT * FROM test_runs WHERE prompt_id = ? ORDER BY created_at DESC",
            (prompt_id,)
        )).fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


@router.post("/benchmark")
async def run_benchmark(req: BenchmarkRequest):
    """Benchmark a prompt on multiple dimensions."""
    result = benchmark.benchmark(req.content)

    # Update prompt effectiveness score if prompt_id provided
    if req.prompt_id:
        db = await get_db()
        try:
            await db.execute(
                "UPDATE prompts SET effectiveness_score = ? WHERE id = ?",
                (result["overall_score"], req.prompt_id),
            )
            await db.commit()
        finally:
            await db.close()

    return result


@router.post("/compare")
async def compare_prompts(prompt_ids: list[int]):
    """Compare test results across multiple prompts."""
    db = await get_db()
    try:
        results = []
        for pid in prompt_ids:
            runs = await (await db.execute(
                "SELECT * FROM test_runs WHERE prompt_id = ? ORDER BY created_at DESC LIMIT 5",
                (pid,)
            )).fetchall()
            prompt = await (await db.execute("SELECT * FROM prompts WHERE id = ?", (pid,))).fetchone()
            if prompt:
                results.append({
                    "prompt_id": pid,
                    "title": prompt["title"],
                    "token_count": prompt["token_count"],
                    "effectiveness_score": prompt["effectiveness_score"],
                    "test_runs": [dict(r) for r in runs],
                })
        return results
    finally:
        await db.close()
