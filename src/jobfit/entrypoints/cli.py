import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path

from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.app.analyze import Analysis, analyze
from jobfit.logging_config import setup_logging

log = logging.getLogger("jobfit.cli")


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
        log.warning("input file missing: %s", path)
        print(f"Файл не найден: {path}")
        return None
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        log.warning("input file is not valid UTF-8: %s", path)
        print(f"Файл не в UTF-8: {path}. Пересохрани его в UTF-8.")
        return None
    log.debug("read %d chars from %s", len(text), path)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(prog="jobfit")
    parser.add_argument("--vacancy", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="уровень логов в stderr (по умолчанию WARNING)",
    )
    args = parser.parse_args()
    setup_logging(args.log_level)

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
