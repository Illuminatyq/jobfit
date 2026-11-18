import ast
import sys
from pathlib import Path

import pytest

METRICS = Path(__file__).resolve().parents[2] / "src" / "jobfit" / "eval" / "metrics.py"
ALLOWED = set(sys.stdlib_module_names)


@pytest.mark.unit
def test_eval_metrics_is_pure() -> None:
    tree = ast.parse(METRICS.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    assert roots <= ALLOWED
