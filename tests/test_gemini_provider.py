import httpx
import pytest
from google.genai._gaos.lib.compat_errors import RateLimitError

from agent_salon.domain import ProviderError, TurnRequest
from agent_salon.providers.gemini import GeminiProvider


class FailingInteractions:
    def create(self, **_kwargs):
        request = httpx.Request("POST", "https://generativelanguage.googleapis.com")
        response = httpx.Response(429, request=request)
        raise RateLimitError("quota exceeded", response=response, body={})


class FailingClient:
    interactions = FailingInteractions()


@pytest.mark.asyncio
async def test_interactions_rate_limit_becomes_clean_provider_error() -> None:
    provider = GeminiProvider("gemini-test", client=FailingClient())
    request = TurnRequest(opening_message="Hello", history=(), instructions="Be yourself")

    with pytest.raises(ProviderError) as caught:
        await provider.respond(request)

    assert caught.value.provider == "Gemini"
    assert caught.value.message == (
        "API quota or rate limit reached. Wait for the quota to reset or check "
        "Gemini API billing and rate limits.\n"
        "Rate-limit documentation: https://ai.google.dev/gemini-api/docs/rate-limits\n"
        "Current usage: https://ai.dev/rate-limit"
    )
