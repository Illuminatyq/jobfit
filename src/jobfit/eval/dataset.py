import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Case:
    id: str
    title: str
    taxonomy_version: str
    vacancy: str
    profile: str
    expected_requirements: dict[str, str]
    expected_confirmed: tuple[str, ...]
    expected_coverage: int
    known_gap: bool = False
    note: str = ""


def load_cases(path: Path) -> list[Case]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    return [
        Case(
            id=str(row["id"]),
            title=str(row["title"]),
            taxonomy_version=str(row["taxonomy_version"]),
            vacancy=str(row["vacancy"]),
            profile=str(row["profile"]),
            expected_requirements={str(k): str(v) for k, v in row["expected_requirements"].items()},
            expected_confirmed=tuple(str(s) for s in row["expected_confirmed"]),
            expected_coverage=int(row["expected_coverage"]),
            known_gap=bool(row.get("known_gap", False)),
            note=str(row.get("note", "")),
        )
        for row in raw["cases"]
    ]
