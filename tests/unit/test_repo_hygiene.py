import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _tracked() -> list[str]:
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        pytest.skip("git repository is not available")
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.splitlines()


@pytest.mark.unit
def test_no_private_data_is_tracked() -> None:
    offenders = [p for p in _tracked() if "private" in Path(p).parts]
    assert not offenders, f"private paths tracked: {offenders}"


@pytest.mark.unit
def test_no_env_or_venv_is_tracked() -> None:
    offenders = [p for p in _tracked() if Path(p).name == ".env" or ".venv" in Path(p).parts]
    assert not offenders, f"forbidden paths tracked: {offenders}"
