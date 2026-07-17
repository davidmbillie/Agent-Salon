from pathlib import Path

import pytest

from agent_salon.bootstrap import initialize_data


def _public_project(root: Path) -> Path:
    project = root / "agent-salon"
    for name in ("personas", "memory", "conversations"):
        directory = project / "templates" / name
        directory.mkdir(parents=True)
        (directory / "README.md").write_text(name, encoding="utf-8")
    (project / "templates" / "data-README.md").write_text("private", encoding="utf-8")
    (project / "config").mkdir()
    (project / "config" / "salon.example.yaml").write_text("session: {}", encoding="utf-8")
    (project / ".env.example").write_text(
        "OPENAI_API_KEY=\nGEMINI_API_KEY=\nSALON_DATA_DIR=old\n", encoding="utf-8"
    )
    return project


def test_initialize_data_copies_templates_and_configures_env(tmp_path: Path) -> None:
    project = _public_project(tmp_path)

    destination = initialize_data(project, Path("../agent-salon-data"))

    assert (destination / "personas" / "README.md").is_file()
    assert (destination / "memory" / "README.md").is_file()
    assert (destination / "conversations" / "README.md").is_file()
    assert (destination / "salon.yaml").is_file()
    assert (destination / "README.md").read_text(encoding="utf-8") == "private"
    assert "SALON_DATA_DIR=../agent-salon-data" in (project / ".env").read_text(
        encoding="utf-8"
    )


def test_initialize_data_refuses_to_overwrite_private_content(tmp_path: Path) -> None:
    project = _public_project(tmp_path)
    destination = tmp_path / "agent-salon-data"
    destination.mkdir()
    (destination / "personal.md").write_text("private", encoding="utf-8")

    with pytest.raises(ValueError, match="Refusing to overwrite"):
        initialize_data(project, destination)
