import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PATTERN = re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}|sk-[A-Za-z0-9_\-]{20,}")
SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "data",
}
SKIP_FILES = {"test_no_secrets.py", ".env"}
SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".json", ".txt", ".cfg", ".ini", ".ps1"}


def _candidates() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in SKIP_FILES:
            continue
        if set(path.parts) & SKIP_DIRS:
            continue
        if path.suffix in SUFFIXES or path.name.startswith(".env."):
            files.append(path)
    return sorted(files)


@pytest.mark.unit
@pytest.mark.parametrize("path", _candidates(), ids=lambda p: str(p.relative_to(ROOT)))
def test_no_hardcoded_secrets(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    assert not PATTERN.search(text), f"secret-like token found in {path}"
