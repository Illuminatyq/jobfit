"""Deterministic, explainable scoring. Pure: stdlib only."""

from jobfit.domain.model import Priority, Requirement

WEIGHTS: dict[Priority, int] = {"must": 3, "nice": 1}


def coverage(requirements: list[Requirement], confirmed: set[str]) -> int:
    total = sum(WEIGHTS[r.priority] for r in requirements)
    if total == 0:
        return 0
    matched = sum(WEIGHTS[r.priority] for r in requirements if r.skill_id in confirmed)
    return round(100 * matched / total)


def gaps(requirements: list[Requirement], confirmed: set[str]) -> list[Requirement]:
    return sorted(
        (r for r in requirements if r.skill_id not in confirmed),
        key=lambda r: (r.priority != "must", r.name),
    )


def critical_gaps(requirements: list[Requirement], confirmed: set[str]) -> list[Requirement]:
    return [r for r in gaps(requirements, confirmed) if r.priority == "must"]
