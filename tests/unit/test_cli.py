import json
import runpy
import sys
from pathlib import Path

import pytest

from jobfit.entrypoints.cli import main


def _write(tmp_path: Path, vacancy: str, profile: str) -> tuple[Path, Path]:
    v = tmp_path / "v.txt"
    p = tmp_path / "p.txt"
    v.write_text(vacancy, encoding="utf-8")
    p.write_text(profile, encoding="utf-8")
    return v, p


def _argv(monkeypatch: pytest.MonkeyPatch, v: Path, p: Path, *extra: str) -> None:
    monkeypatch.setattr(sys, "argv", ["jobfit", "--vacancy", str(v), "--profile", str(p), *extra])


@pytest.mark.unit
def test_cli_human_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    vacancy_text: str,
    profile_text: str,
) -> None:
    v, p = _write(tmp_path, vacancy_text, profile_text)
    _argv(monkeypatch, v, p)
    assert main() == 0
    out = capsys.readouterr().out
    assert "Покрытие: 55%" in out
    assert "Что дописать в резюме" in out


@pytest.mark.unit
def test_cli_json_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    vacancy_text: str,
    profile_text: str,
) -> None:
    v, p = _write(tmp_path, vacancy_text, profile_text)
    _argv(monkeypatch, v, p, "--json")
    assert main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coverage"] == 55
    assert payload["taxonomy_version"] == "1.0.0"
    assert payload["confirmed"] == ["mysql", "postman"]


@pytest.mark.unit
def test_cli_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    profile_text: str,
) -> None:
    p = tmp_path / "p.txt"
    p.write_text(profile_text, encoding="utf-8")
    _argv(monkeypatch, tmp_path / "nope.txt", p)
    assert main() == 2
    assert "Файл не найден" in capsys.readouterr().out


@pytest.mark.unit
def test_cli_non_utf8_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    v = tmp_path / "v.txt"
    v.write_bytes(b"\xff\xfe\x00bad")
    p = tmp_path / "p.txt"
    p.write_text("Postman", encoding="utf-8")
    _argv(monkeypatch, v, p)
    assert main() == 2
    assert "UTF-8" in capsys.readouterr().out


@pytest.mark.unit
def test_cli_handles_bom(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    vacancy_text: str,
    profile_text: str,
) -> None:
    v = tmp_path / "v.txt"
    v.write_bytes(b"\xef\xbb\xbf" + vacancy_text.encode("utf-8"))
    p = tmp_path / "p.txt"
    p.write_text(profile_text, encoding="utf-8")
    _argv(monkeypatch, v, p)
    assert main() == 0
    assert "Покрытие: 55%" in capsys.readouterr().out


@pytest.mark.unit
def test_module_entrypoint(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    vacancy_text: str,
    profile_text: str,
) -> None:
    v, p = _write(tmp_path, vacancy_text, profile_text)
    _argv(monkeypatch, v, p)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("jobfit.entrypoints.cli", run_name="__main__")
    assert exc.value.code == 0
    assert "Покрытие: 55%" in capsys.readouterr().out
