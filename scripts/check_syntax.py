import ast
import pathlib
import sys

bad: list[str] = []
for path in pathlib.Path().rglob("*.py"):
    if ".venv" in path.parts:
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        bad.append(f"{path}:{exc.lineno}: {exc.msg}")
    except UnicodeDecodeError as exc:
        bad.append(f"{path}: encoding: {exc}")

print("\n".join(bad) if bad else "all files parse OK")
sys.exit(1 if bad else 0)
