import ast
import sys
from pathlib import Path

import pytest

DOMAIN_DIR = Path(__file__).resolve().parents[2] / "src" / "jobfit" / "domain"
ALLOWED = set(sys.stdlib_module_names) | {"jobfit"}


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


@pytest.mark.unit
def test_domain_layer_is_not_empty() -> None:
    modules = [p for p in DOMAIN_DIR.glob("*.py") if p.name != "__init__.py"]
    assert len(modules) >= 5, "domain must contain real logic"


@pytest.mark.unit
@pytest.mark.parametrize("path", sorted(DOMAIN_DIR.glob("*.py")), ids=lambda p: p.name)
def test_domain_depends_only_on_stdlib_and_itself(path: Path) -> None:
    assert _imported_roots(path) <= ALLOWED
