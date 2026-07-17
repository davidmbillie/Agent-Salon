from dataclasses import dataclass
from pathlib import Path

from agent_salon.domain import Conversation, Turn
from agent_salon.transcript import load_conversation, next_provider, save_conversation


@dataclass
class Participant:
    name: str
    model: str = "fake-model"


def test_structured_conversation_round_trip(tmp_path: Path) -> None:
    original = Conversation(
        opening_message="Begin here",
        turns=[Turn("OpenAI", "Hello"), Turn("Gemini", "## A nested heading\n\nHello back")],
    )
    session = save_conversation(
        tmp_path,
        original,
        (Participant("OpenAI"), Participant("Gemini")),
    )

    loaded, lineage = load_conversation(session)

    assert loaded == original
    assert lineage == session.name


def test_existing_markdown_transcript_can_be_loaded(tmp_path: Path) -> None:
    session = tmp_path / "old-session"
    session.mkdir()
    (session / "transcript.md").write_text(
        "# Conversation\n\n## Curator\n\nBegin\n\n"
        "## OpenAI\n\nFirst\n\n## Detail\n\nStill first\n\n"
        "## Gemini\n\nSecond\n",
        encoding="utf-8",
    )

    loaded, _ = load_conversation(session)

    assert loaded.opening_message == "Begin"
    assert loaded.turns[0].text == "First\n\n## Detail\n\nStill first"
    assert next_provider(loaded, "gemini") == "openai"


def test_curator_message_does_not_change_the_next_provider() -> None:
    conversation = Conversation(
        opening_message="Begin",
        turns=[Turn("OpenAI", "First"), Turn("Gemini", "Second")],
    )
    conversation.turns.append(Turn("Curator", "Let us continue with the ceremony"))

    assert next_provider(conversation, "gemini") == "openai"
