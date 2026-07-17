from dataclasses import dataclass

import pytest

from agent_salon.domain import TurnRequest, TurnResponse
from agent_salon.orchestrator import relay


@dataclass
class FakeProvider:
    name: str
    model: str = "fake-model"

    async def respond(self, request: TurnRequest) -> TurnResponse:
        return TurnResponse(
            text=f"response {len(request.history) + 1}",
            provider=self.name,
            model=self.model,
        )


@pytest.mark.asyncio
async def test_relay_alternates_participants_and_stops_at_limit() -> None:
    openai = FakeProvider("OpenAI")
    gemini = FakeProvider("Gemini")
    conversation = await relay(
        opening_message="Hello",
        participants=(openai, gemini),
        instructions={"OpenAI": "Be yourself", "Gemini": "Be yourself"},
        max_turns=3,
    )
    assert [turn.speaker for turn in conversation.turns] == ["OpenAI", "Gemini", "OpenAI"]
    assert [turn.text for turn in conversation.turns] == ["response 1", "response 2", "response 3"]


@pytest.mark.asyncio
async def test_relay_rejects_zero_turn_limit() -> None:
    provider = FakeProvider("OpenAI")
    with pytest.raises(ValueError, match="at least 1"):
        await relay("Hello", (provider, provider), {"OpenAI": ""}, 0)
