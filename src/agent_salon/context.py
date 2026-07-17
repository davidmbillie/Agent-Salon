from pathlib import Path

from agent_salon.config import ParticipantConfig, SalonConfig


def build_instructions(config: SalonConfig, participant: ParticipantConfig) -> str:
    sections = (
        ("Persona", participant.persona),
        ("Private continuity", participant.private_memory),
        ("Shared continuity", config.shared_memory),
        ("Conversation mode", config.project_dir / "prompts" / f"{config.mode}.md"),
    )
    return "\n\n".join(f"# {title}\n\n{_read(path)}" for title, path in sections)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()
