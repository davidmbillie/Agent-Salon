from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Turn:
    speaker: str
    text: str


@dataclass(frozen=True, slots=True)
class TurnRequest:
    opening_message: str
    history: tuple[Turn, ...]
    instructions: str

    def as_prompt(self) -> str:
        transcript = "\n\n".join(f"{turn.speaker}: {turn.text}" for turn in self.history)
        return (
            f"The curator opened with:\n{self.opening_message}\n\n"
            f"Conversation so far:\n{transcript}\n\n"
            "Continue the conversation with one natural response."
        )


@dataclass(frozen=True, slots=True)
class TurnResponse:
    text: str
    provider: str
    model: str


@dataclass(slots=True)
class Conversation:
    opening_message: str
    turns: list[Turn] = field(default_factory=list)


class Provider(Protocol):
    name: str
    model: str

    async def respond(self, request: TurnRequest) -> TurnResponse: ...
