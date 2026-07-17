from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from agent_salon.domain import Conversation, Provider, ProviderError


def save_conversation(
    data_dir: Path,
    conversation: Conversation,
    participants: tuple[Provider, Provider],
    error: ProviderError | None = None,
) -> Path:
    now = datetime.now(timezone.utc)
    session_dir = data_dir / "conversations" / now.strftime("%Y-%m-%d-%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=False)

    transcript = ["# Conversation", "", "## Curator", "", conversation.opening_message]
    for turn in conversation.turns:
        transcript.extend(("", f"## {turn.speaker}", "", turn.text))
    (session_dir / "transcript.md").write_text("\n".join(transcript) + "\n", encoding="utf-8")

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
    (session_dir / "metadata.yaml").write_text(
        yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8"
    )
    return session_dir
