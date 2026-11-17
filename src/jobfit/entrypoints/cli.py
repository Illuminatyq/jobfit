import argparse
import json
from dataclasses import asdict
from pathlib import Path

from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.app.analyze import Analysis, analyze


def _print_human(result: Analysis) -> None:
    print(f"Покрытие: {result.coverage}%  (словарь {result.taxonomy_version})")
    print(f"Требований: {len(result.requirements)}, подтверждено: {len(result.confirmed)}")
    print("\nКритичные пробелы:")
    for item in result.critical_gaps:
        print(f"  - {item.name}")
    print("\nВсе пробелы:")
    for item in result.gaps:
        mark = "must" if item.priority == "must" else "nice"
        print(f"  - [{mark}] {item.name}")
    print("\nЧто дописать в резюме:")
    for hint in result.hints:
        print(f"  - {hint}")


def _read(path: Path) -> str | None:
    if not path.is_file():
        print(f"Файл не найден: {path}")
        return None
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        print(f"Файл не в UTF-8: {path}. Пересохрани его в UTF-8.")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(prog="jobfit")
    parser.add_argument("--vacancy", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    vacancy = _read(args.vacancy)
    profile = _read(args.profile)
    if vacancy is None or profile is None:
        return 2

    result = analyze(vacancy, profile, load_default_taxonomy())
    if args.as_json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
