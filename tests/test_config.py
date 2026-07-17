from pathlib import Path

from agent_salon.config import load_config, validate_config


def test_repository_configuration_is_valid(monkeypatch) -> None:
    project_dir = Path(__file__).parents[1]
    monkeypatch.setenv("SALON_DATA_DIR", str(project_dir.parent / "agent-salon-data"))
    config = load_config(project_dir)
    assert config.max_turns == 6
    assert config.start_with == "openai"
    assert config.pause_between_relays is True
    assert validate_config(config) == []
