from dataclasses import dataclass
from typing import Literal

Priority = Literal["must", "nice"]


@dataclass(frozen=True, slots=True)
class Match:
    skill_id: str
    start: int
    end: int
    alias: str


@dataclass(frozen=True, slots=True)
class Requirement:
    skill_id: str
    name: str
    priority: Priority
    snippet: str


@dataclass(frozen=True, slots=True)
class Evidence:
    id: str
    text: str
    skills: tuple[str, ...]
