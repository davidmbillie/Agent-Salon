from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class ParticipantConfig:
    model: str
    persona: Path
    private_memory: Path


@dataclass(frozen=True, slots=True)
class SalonConfig:
    project_dir: Path
    data_dir: Path
    mode: str
    max_turns: int
    openai: ParticipantConfig
    gemini: ParticipantConfig
    shared_memory: Path


def load_config(project_dir: Path | None = None) -> SalonConfig:
    project_dir = (project_dir or Path.cwd()).resolve()
    load_dotenv(project_dir / ".env")
    data_dir_value = os.getenv("SALON_DATA_DIR")
    if not data_dir_value:
        raise ValueError("SALON_DATA_DIR is missing; copy .env.example to .env and set it")

    data_dir = Path(data_dir_value)
    if not data_dir.is_absolute():
        data_dir = project_dir / data_dir
    data_dir = data_dir.resolve()

    raw = _read_yaml(data_dir / "salon.yaml")
    participants = _mapping(raw, "participants")
    session = _mapping(raw, "session")
    return SalonConfig(
        project_dir=project_dir,
        data_dir=data_dir,
        mode=str(session.get("mode", "relay")),
        max_turns=int(session.get("max_turns", 6)),
        openai=_participant(data_dir, _mapping(participants, "openai")),
        gemini=_participant(data_dir, _mapping(participants, "gemini")),
        shared_memory=_data_path(data_dir, raw, "shared_memory"),
    )


def validate_config(config: SalonConfig) -> list[str]:
    errors: list[str] = []
    if config.max_turns < 1:
        errors.append("session.max_turns must be at least 1")
    required = (
        config.openai.persona,
        config.openai.private_memory,
        config.gemini.persona,
        config.gemini.private_memory,
        config.shared_memory,
        config.project_dir / "prompts" / f"{config.mode}.md",
    )
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path}")
    return errors


def _participant(data_dir: Path, raw: dict[str, Any]) -> ParticipantConfig:
    if "model" not in raw:
        raise ValueError("Each participant requires a model")
    return ParticipantConfig(
        model=str(raw["model"]),
        persona=_data_path(data_dir, raw, "persona"),
        private_memory=_data_path(data_dir, raw, "private_memory"),
    )


def _data_path(data_dir: Path, raw: dict[str, Any], key: str) -> Path:
    if key not in raw:
        raise ValueError(f"Missing configuration value: {key}")
    path = Path(str(raw[key]))
    return path if path.is_absolute() else data_dir / path


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Configuration file does not exist: {path}")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def _mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' to be a mapping")
    return value
