import asyncio
from typing import Any

from google import genai
from google.genai._gaos.lib.compat_errors import (
    APIConnectionError as InteractionsConnectionError,
)
from google.genai._gaos.lib.compat_errors import APIError as InteractionsAPIError
from google.genai._gaos.lib.compat_errors import (
    AuthenticationError as InteractionsAuthenticationError,
)
from google.genai._gaos.lib.compat_errors import RateLimitError as InteractionsRateLimitError
from google.genai.errors import APIError

from agent_salon.domain import ProviderError, TurnRequest, TurnResponse


class GeminiProvider:
    name = "Gemini"

    def __init__(self, model: str, client: Any | None = None) -> None:
        self.model = model
        self._client = client or genai.Client()

    async def respond(self, request: TurnRequest) -> TurnResponse:
        try:
            interaction = await asyncio.to_thread(
                self._client.interactions.create,
                model=self.model,
                input=request.as_prompt(),
                system_instruction=request.instructions,
                store=False,
            )
        except InteractionsRateLimitError as error:
            raise ProviderError(
                self.name,
                "API quota or rate limit reached. Wait for the quota to reset or check "
                "Gemini API billing and rate limits.\n"
                "Rate-limit documentation: https://ai.google.dev/gemini-api/docs/rate-limits\n"
                "Current usage: https://ai.dev/rate-limit",
            ) from error
        except InteractionsAuthenticationError as error:
            raise ProviderError(self.name, "API key was rejected. Check GEMINI_API_KEY.") from error
        except InteractionsConnectionError as error:
            raise ProviderError(self.name, "Could not connect to the Gemini API.") from error
        except (APIError, InteractionsAPIError) as error:
            status = getattr(error, "status_code", None)
            detail = f" with status {status}" if status else ""
            raise ProviderError(
                self.name, f"API request failed{detail}."
            ) from error
        text = interaction.output_text.strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return TurnResponse(text=text, provider=self.name, model=self.model)
