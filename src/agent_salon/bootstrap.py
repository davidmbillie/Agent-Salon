from __future__ import annotations

import os
import shutil
from pathlib import Path


def initialize_data(project_dir: Path, destination: Path) -> Path:
    project_dir = project_dir.resolve()
    if not destination.is_absolute():
        destination = project_dir / destination
    destination = destination.resolve()

    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Refusing to overwrite non-empty private data directory: {destination}")

    template_dir = project_dir / "templates"
    config_template = project_dir / "config" / "salon.example.yaml"
    required = (
        template_dir / "personas",
        template_dir / "memory",
        template_dir / "conversations",
        template_dir / "data-README.md",
        config_template,
    )
    missing = [path for path in required if not path.exists()]
    if missing:
        raise ValueError(f"Missing public setup template: {missing[0]}")

    destination.mkdir(parents=True, exist_ok=True)
    for name in ("personas", "memory", "conversations"):
        shutil.copytree(template_dir / name, destination / name, dirs_exist_ok=True)
    shutil.copy2(template_dir / "data-README.md", destination / "README.md")
    shutil.copy2(config_template, destination / "salon.yaml")
    _set_data_directory(project_dir, destination)
    return destination


def _set_data_directory(project_dir: Path, destination: Path) -> None:
    env_path = project_dir / ".env"
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    else:
        example = project_dir / ".env.example"
        lines = example.read_text(encoding="utf-8").splitlines() if example.is_file() else []

    relative = Path(os.path.relpath(destination, project_dir)).as_posix()
    setting = f"SALON_DATA_DIR={relative}"
    for index, line in enumerate(lines):
        if line.startswith("SALON_DATA_DIR="):
            lines[index] = setting
            break
    else:
        lines.append(setting)
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
