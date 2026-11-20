"""Регрессия на агентский дрейф: артефакты и приватные данные не должны попадать в git."""

import subprocess

import pytest


def _tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
    return result.stdout.splitlines()


@pytest.mark.unit
def test_no_bytecode_tracked() -> None:
    bad = [f for f in _tracked_files() if "__pycache__" in f or f.endswith((".pyc", ".pyo"))]
    assert bad == [], f"tracked bytecode: {bad}"


@pytest.mark.unit
def test_no_generated_or_private_tracked() -> None:
    prefixes = ("reports/", "allure-", "venv/", ".venv/", "data/private/")
    bad = [f for f in _tracked_files() if f.startswith(prefixes)]
    assert bad == [], f"tracked forbidden paths: {bad}"
