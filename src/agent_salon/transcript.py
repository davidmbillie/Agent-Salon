from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from agent_salon.domain import Conversation, Provider, ProviderError, Turn

SPEAKERS = {"Curator", "OpenAI", "Gemini"}


def save_conversation(
    data_dir: Path,
    conversation: Conversation,
    participants: tuple[Provider, Provider],
    error: ProviderError | None = None,
    resumed_from: str | None = None,
) -> Path:
    now = datetime.now(timezone.utc)
    session_dir = data_dir / "conversations" / now.strftime("%Y-%m-%d-%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=False)

    transcript = ["# Conversation", "", "## Curator", "", conversation.opening_message]
    for turn in conversation.turns:
        transcript.extend(("", f"## {turn.speaker}", "", turn.text))
    (session_dir / "transcript.md").write_text("\n".join(transcript) + "\n", encoding="utf-8")

    structured = {
        "opening_message": conversation.opening_message,
        "turns": [
            {"speaker": turn.speaker, "text": turn.text} for turn in conversation.turns
        ],
    }
    (session_dir / "conversation.yaml").write_text(
        yaml.safe_dump(structured, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    metadata = {
        "started_at": now.isoformat(),
        "turns": len(conversation.turns),
        "participants": [
            {"provider": participant.name, "model": participant.model}
            for participant in participants
        ],
    }
    if error:
        metadata["interrupted"] = {"provider": error.provider, "message": error.message}
    if resumed_from:
        metadata["resumed_from"] = resumed_from
    (session_dir / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
    )
    return session_dir


def load_conversation(source: Path) -> tuple[Conversation, str]:
    source = source.resolve()
    if source.is_dir():
        structured = source / "conversation.yaml"
        markdown = source / "transcript.md"
        path = structured if structured.is_file() else markdown
        lineage = source.name
    else:
        path = source
        lineage = source.parent.name

    if not path.is_file():
        raise ValueError(f"Conversation source does not exist: {path}")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(path), lineage
    if path.suffix.lower() == ".md":
        return _load_markdown(path), lineage
    raise ValueError("Resume source must be a session directory, Markdown, or YAML file")


def next_provider(conversation: Conversation, default: str) -> str:
    for turn in reversed(conversation.turns):
        if turn.speaker == "OpenAI":
            return "gemini"
        if turn.speaker == "Gemini":
            return "openai"
    return default


def _load_yaml(path: Path) -> Conversation:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("opening_message"), str):
        raise ValueError(f"Invalid structured conversation: {path}")
    raw_turns = raw.get("turns")
    if not isinstance(raw_turns, list):
        raise ValueError(f"Conversation turns must be a list: {path}")
    turns: list[Turn] = []
    for item in raw_turns:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid turn in {path}")
        speaker, text = item.get("speaker"), item.get("text")
        if speaker not in SPEAKERS or not isinstance(text, str):
            raise ValueError(f"Invalid speaker or text in {path}")
        turns.append(Turn(speaker=speaker, text=text))
    return Conversation(opening_message=raw["opening_message"], turns=turns)


def _load_markdown(path: Path) -> Conversation:
    sections: list[tuple[str, str]] = []
    speaker: str | None = None
    body: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        candidate = line.removeprefix("## ") if line.startswith("## ") else None
        if candidate in SPEAKERS:
            if speaker is not None:
                sections.append((speaker, "\n".join(body).strip()))
            speaker = candidate
            body = []
        elif speaker is not None:
            body.append(line)
    if speaker is not None:
        sections.append((speaker, "\n".join(body).strip()))

    if not sections or sections[0][0] != "Curator" or not sections[0][1]:
        raise ValueError(f"Transcript must begin with a non-empty Curator section: {path}")
    turns = [Turn(speaker=name, text=text) for name, text in sections[1:] if text]
    return Conversation(opening_message=sections[0][1], turns=turns)
