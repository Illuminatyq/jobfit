"""Loading and validating the golden evaluation dataset. Pure: stdlib only."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class Case:
    id: str
    vacancy: str
    profile: str
    expected_requirements: tuple[tuple[str, str], ...]
    expected_confirmed: frozenset[str]


def _require(payload: dict[str, Any], key: str, path: Path) -> Any:
    if key not in payload:
        raise ValueError(f"{path}: missing required key {key!r}")
    return payload[key]


def parse_case(raw: dict[str, Any], path: Path) -> Case:
    case_id = str(_require(raw, "id", path))
    vacancy = str(_require(raw, "vacancy", path))
    profile = str(_require(raw, "profile", path))
    reqs_raw = _require(raw, "expected_requirements", path)
    if not isinstance(reqs_raw, list):
        raise ValueError(f"{path}: case {case_id}: expected_requirements must be a list")
    requirements: list[tuple[str, str]] = []
    for item in reqs_raw:
        skill_id = str(item["skill_id"])
        priority = str(item["priority"])
        if priority not in {"must", "nice"}:
            raise ValueError(f"{path}: case {case_id}: bad priority {priority!r}")
        requirements.append((skill_id, priority))
    confirmed_raw = _require(raw, "expected_confirmed", path)
    if not isinstance(confirmed_raw, list):
        raise ValueError(f"{path}: case {case_id}: expected_confirmed must be a list")
    return Case(
        id=case_id,
        vacancy=vacancy,
        profile=profile,
        expected_requirements=tuple(requirements),
        expected_confirmed=frozenset(str(s) for s in confirmed_raw),
    )


def load_cases(path: Path) -> list[Case]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = raw.get("cases", []) if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{path}: no cases found in golden dataset")
    return [parse_case(row, path) for row in rows]
