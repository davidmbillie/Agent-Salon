from pathlib import Path

import pytest

from agent_salon.curator_input import read_text_file


def test_read_text_file_preserves_markdown(tmp_path: Path, capsys) -> None:
    path = tmp_path / "message.md"
    content = "# Long opening\n\nA precise thought.\n"
    path.write_text(content, encoding="utf-8")

    result = read_text_file(path)

    assert result == content
    assert f"Loaded {len(content)} characters from message.md" in capsys.readouterr().out


def test_read_text_file_accepts_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "message.md"
    path.write_text("A thought", encoding="utf-8-sig")

    assert read_text_file(path) == "A thought"


def test_read_text_file_rejects_empty_content(tmp_path: Path) -> None:
    path = tmp_path / "empty.md"
    path.write_text("  \n", encoding="utf-8")

    with pytest.raises(ValueError, match="is empty"):
        read_text_file(path)
