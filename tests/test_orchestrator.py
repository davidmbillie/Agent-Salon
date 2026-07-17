from dataclasses import dataclass

import pytest

from agent_salon.domain import ProviderError, TurnRequest, TurnResponse
from agent_salon.orchestrator import RelayInterrupted, relay


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


@dataclass
class FailingProvider:
    name: str
    model: str = "fake-model"

    async def respond(self, request: TurnRequest) -> TurnResponse:
        raise ProviderError(self.name, "quota unavailable")


@pytest.mark.asyncio
async def test_relay_exposes_partial_conversation_when_provider_fails() -> None:
    gemini = FakeProvider("Gemini")
    openai = FailingProvider("OpenAI")

    with pytest.raises(RelayInterrupted) as caught:
        await relay(
            "Hello",
            (gemini, openai),
            {"Gemini": "", "OpenAI": ""},
            max_turns=3,
        )

    assert [turn.speaker for turn in caught.value.conversation.turns] == ["Gemini"]
    assert caught.value.error.provider == "OpenAI"


@pytest.mark.asyncio
async def test_relay_adds_curator_input_after_each_complete_pair() -> None:
    openai = FakeProvider("OpenAI")
    gemini = FakeProvider("Gemini")

    conversation = await relay(
        "Hello",
        (openai, gemini),
        {"OpenAI": "", "Gemini": ""},
        max_turns=4,
        on_relay_complete=lambda _: "A curator thought",
    )

    assert [turn.speaker for turn in conversation.turns] == [
        "OpenAI",
        "Gemini",
        "Curator",
        "OpenAI",
        "Gemini",
    ]


@pytest.mark.asyncio
async def test_curator_can_end_after_a_complete_pair() -> None:
    openai = FakeProvider("OpenAI")
    gemini = FakeProvider("Gemini")

    conversation = await relay(
        "Hello",
        (openai, gemini),
        {"OpenAI": "", "Gemini": ""},
        max_turns=6,
        on_relay_complete=lambda _: None,
    )

    assert [turn.speaker for turn in conversation.turns] == ["OpenAI", "Gemini"]
