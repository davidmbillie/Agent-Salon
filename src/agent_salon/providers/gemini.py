import asyncio
from typing import Any

from google import genai
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
        except APIError as error:
            raise ProviderError(
                self.name, f"API request failed: {getattr(error, 'message', 'unknown error')}"
            ) from error
        text = interaction.output_text.strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return TurnResponse(text=text, provider=self.name, model=self.model)
