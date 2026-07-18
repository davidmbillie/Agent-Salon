from pathlib import Path


def read_text_file(path: Path) -> str:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"Curator message file does not exist: {path}")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"Curator message file must be UTF-8: {path}") from error
    if not text.strip():
        raise ValueError(f"Curator message file is empty: {path}")
    print(f"Loaded {len(text):,} characters from {path.name}")
    return text
