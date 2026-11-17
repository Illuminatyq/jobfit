"""Skill taxonomy and boundary-aware matching. Pure: stdlib only."""

import re
from dataclasses import dataclass
from typing import Any

from jobfit.domain.model import Match
from jobfit.domain.normalize import normalize_for_match

_LEFT = r"(?<![^\W_])"
_RIGHT = r"(?![^\W_])"
_LANG_CUE = re.compile(r"golang|язык|python|java|kotlin|backend|бэкенд|разработк")


@dataclass(frozen=True, slots=True)
class Skill:
    id: str
    name: str
    category: str
    aliases: tuple[str, ...]
    guarded: bool = False


class Taxonomy:
    def __init__(self, version: str, skills: tuple[Skill, ...]) -> None:
        self.version = version
        self.skills = skills
        self.names = {skill.id: skill.name for skill in skills}
        self._lang_aliases = tuple(
            alias
            for skill in skills
            if skill.category == "lang" and not skill.guarded
            for alias in skill.aliases
        )
        self._patterns = {
            skill.id: tuple(
                (alias, re.compile(_LEFT + re.escape(normalize_for_match(alias)) + _RIGHT))
                for alias in skill.aliases
            )
            for skill in skills
        }

    def _guard_ok(self, text: str, start: int, end: int) -> bool:
        window = text[max(0, start - 60) : end + 60]
        if _LANG_CUE.search(window):
            return True
        return any(alias in window for alias in self._lang_aliases)

    def find(self, text: str) -> list[Match]:
        hay = normalize_for_match(text)
        found: list[Match] = []
        for skill in self.skills:
            hits: list[Match] = []
            for alias, pattern in self._patterns[skill.id]:
                hits.extend(
                    Match(skill.id, m.start(), m.end(), alias) for m in pattern.finditer(hay)
                )
            if not hits:
                continue
            if skill.guarded and not any(self._guard_ok(hay, h.start, h.end) for h in hits):
                continue
            found.append(min(hits, key=lambda h: (h.start, h.alias)))
        return sorted(found, key=lambda m: (m.start, m.skill_id))


def build_taxonomy(version: str, rows: list[dict[str, Any]]) -> Taxonomy:
    skills = tuple(
        Skill(
            id=str(row["id"]),
            name=str(row["name"]),
            category=str(row["category"]),
            aliases=tuple(str(a) for a in row["aliases"]),
            guarded=bool(row.get("guarded", False)),
        )
        for row in rows
    )
    return Taxonomy(version, skills)
