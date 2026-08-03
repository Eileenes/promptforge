"""Configuration for PromptForge."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PromptForge"
    app_version: str = "1.0.0"
    database_url: str = "data/promptforge.db"
    # LLM provider API keys (all optional - works in demo mode without them)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    # Default optimization strategy
    default_optimization_level: str = "balanced"  # minimal, balanced, aggressive
    # Token counting model
    token_encoding: str = "cl100k_base"

    class Config:
        env_file = ".env"


settings = Settings()
