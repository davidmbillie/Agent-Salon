from openai import AsyncOpenAI

from agent_salon.domain import TurnRequest, TurnResponse


class OpenAIProvider:
    name = "OpenAI"

    def __init__(self, model: str, client: AsyncOpenAI | None = None) -> None:
        self.model = model
        self._client = client or AsyncOpenAI()

    async def respond(self, request: TurnRequest) -> TurnResponse:
        response = await self._client.responses.create(
            model=self.model,
            instructions=request.instructions,
            input=request.as_prompt(),
            store=False,
        )
        text = response.output_text.strip()
        if not text:
            raise RuntimeError("OpenAI returned an empty response")
        return TurnResponse(text=text, provider=self.name, model=self.model)
