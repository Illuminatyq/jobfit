"""Requirement extraction and evidence indexing. Pure: stdlib only."""

import re

from jobfit.domain.model import Evidence, Match, Priority, Requirement
from jobfit.domain.normalize import normalize, normalize_for_match
from jobfit.domain.taxonomy import Taxonomy

_SPLIT = re.compile(r"[\n\r]+|(?<=[.!?;])\s+")
_NICE = ("будет плюсом", "желательно", "nice to have", "плюсом", "необязательно", "приветствуется")
_MUST = ("обязательно", "must have", "требуется", "необходимо", "обязателен")
_REQ_HEADER = ("требован", "навыки", "ожидаем", "что нужно", "qualifications", "requirements")
_OFFER_HEADER = ("условия", "мы предлагаем", "что мы предлагаем", "benefits", "что получишь")
_SKIP_HEADER = ("обязанности", "задачи", "чем предстоит", "responsibilities")


def segments(text: str) -> list[str]:
    return [part.strip() for part in _SPLIT.split(normalize(text)) if part.strip()]


def _header_kind(segment: str) -> str | None:
    low = normalize_for_match(segment)
    if len(low) > 60:
        return None
    if any(marker in low for marker in _OFFER_HEADER):
        return "offer"
    if any(marker in low for marker in _SKIP_HEADER):
        return "skip"
    if any(marker in low for marker in _REQ_HEADER):
        return "req"
    return None


def _priority(segment: str, section: str | None) -> Priority | None:
    low = normalize_for_match(segment)
    if any(marker in low for marker in _NICE):
        return "nice"
    if any(marker in low for marker in _MUST):
        return "must"
    if section in {"offer", "skip"}:
        return None
    return "must"


def extract_requirements(text: str, taxonomy: Taxonomy) -> list[Requirement]:
    section: str | None = None
    seen: dict[str, Requirement] = {}
    for segment in segments(text):
        kind = _header_kind(segment)
        if kind is not None:
            section = kind
        priority = _priority(segment, section)
        if priority is None:
            continue
        for match in taxonomy.find(segment):
            _keep(seen, match, priority, segment, taxonomy)
    return sorted(seen.values(), key=lambda r: r.skill_id)


def _keep(
    seen: dict[str, Requirement],
    match: Match,
    priority: Priority,
    segment: str,
    taxonomy: Taxonomy,
) -> None:
    existing = seen.get(match.skill_id)
    if existing is not None and (existing.priority == "must" or priority == "nice"):
        return
    seen[match.skill_id] = Requirement(
        skill_id=match.skill_id,
        name=taxonomy.names[match.skill_id],
        priority=priority,
        snippet=segment,
    )


def extract_evidence(text: str, taxonomy: Taxonomy) -> list[Evidence]:
    items: list[Evidence] = []
    for segment in segments(text):
        ids = sorted({match.skill_id for match in taxonomy.find(segment)})
        if ids:
            items.append(Evidence(f"e{len(items) + 1}", segment, tuple(ids)))
    return items


def confirmed_skills(evidence: list[Evidence]) -> set[str]:
    return {skill for item in evidence for skill in item.skills}
