"""Multi-model LLM provider service for PromptForge.

Supports OpenAI, Anthropic Claude, and a mock provider for demo mode.
Inspired by the multi-model trend in AI tools (Open WebUI, big-AGI).
"""
import time
import httpx
from config import settings


class LLMProvider:
    """Unified interface for multiple LLM providers."""

    PROVIDERS = {
        "openai": {
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "label": "OpenAI GPT",
        },
        "anthropic": {
            "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
            "label": "Anthropic Claude",
        },
        "mock": {
            "models": ["mock-standard", "mock-fast"],
            "label": "Mock (Demo Mode)",
        },
    }

    async def call_openai(self, prompt: str, model: str, api_key: str = None) -> dict:
        """Call OpenAI API."""
        key = api_key or settings.openai_api_key
        if not key:
            return await self._mock_response(prompt, model)

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "output": data["choices"][0]["message"]["content"],
                "tokens_input": data["usage"]["prompt_tokens"],
                "tokens_output": data["usage"]["completion_tokens"],
            }

    async def call_anthropic(self, prompt: str, model: str, api_key: str = None) -> dict:
        """Call Anthropic API."""
        key = api_key or settings.anthropic_api_key
        if not key:
            return await self._mock_response(prompt, model)

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "output": data["content"][0]["text"],
                "tokens_input": data["usage"]["input_tokens"],
                "tokens_output": data["usage"]["output_tokens"],
            }

    async def _mock_response(self, prompt: str, model: str) -> dict:
        """Generate a mock response for demo mode (no API key needed)."""
        # Simulate processing time
        await time.sleep(0.3)
        mock_output = (
            f"[Mock Response from {model}]\n\n"
            f"Received prompt ({len(prompt)} chars). In production mode with a valid API key, "
            f"this would return an actual LLM response. The prompt content would be processed "
            f"and a contextual response generated.\n\n"
            f"Prompt preview: {prompt[:200]}..."
        )
        return {
            "output": mock_output,
            "tokens_input": len(prompt.split()),
            "tokens_output": len(mock_output.split()),
        }

    async def call(self, provider: str, model: str, prompt: str, input_text: str = "") -> dict:
        """Call the specified provider with the prompt + input text."""
        full_prompt = f"{prompt}\n\nInput:\n{input_text}" if input_text else prompt
        start = time.time()

        if provider == "openai":
            result = await self.call_openai(full_prompt, model)
        elif provider == "anthropic":
            result = await self.call_anthropic(full_prompt, model)
        else:
            result = await self._mock_response(full_prompt, model)

        latency_ms = int((time.time() - start) * 1000)
        result["latency_ms"] = latency_ms
        return result

    def list_providers(self) -> dict:
        """List available providers and their models."""
        return self.PROVIDERS


llm_provider = LLMProvider()
