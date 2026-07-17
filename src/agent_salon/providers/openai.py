from openai import APIConnectionError, APIStatusError, AsyncOpenAI, AuthenticationError, RateLimitError

from agent_salon.domain import ProviderError, TurnRequest, TurnResponse


class OpenAIProvider:
    name = "OpenAI"

    def __init__(self, model: str, client: AsyncOpenAI | None = None) -> None:
        self.model = model
        self._client = client or AsyncOpenAI()

    async def respond(self, request: TurnRequest) -> TurnResponse:
        try:
            response = await self._client.responses.create(
                model=self.model,
                instructions=request.instructions,
                input=request.as_prompt(),
                store=False,
            )
        except RateLimitError as error:
            raise ProviderError(
                self.name,
                "API quota is unavailable. Check OpenAI API billing and usage limits.",
            ) from error
        except AuthenticationError as error:
            raise ProviderError(self.name, "API key was rejected. Check OPENAI_API_KEY.") from error
        except APIConnectionError as error:
            raise ProviderError(self.name, "Could not connect to the OpenAI API.") from error
        except APIStatusError as error:
            raise ProviderError(
                self.name, f"API request failed with status {error.status_code}."
            ) from error
        text = response.output_text.strip()
        if not text:
            raise RuntimeError("OpenAI returned an empty response")
        return TurnResponse(text=text, provider=self.name, model=self.model)
