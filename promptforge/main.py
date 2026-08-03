"""PromptForge - AI Prompt Engineering Toolkit

Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from config import settings
from database import init_db
from routers import prompts, optimize, test, library


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Prompt Engineering Toolkit - Optimize, Test, and Manage Your Prompts",
    lifespan=lifespan,
)

# Register API routers
app.include_router(prompts.router)
app.include_router(optimize.router)
app.include_router(test.router)
app.include_router(library.router)


# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def index():
    """Serve the main web UI."""
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8777, reload=True)
