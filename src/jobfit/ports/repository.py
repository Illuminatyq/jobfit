"""Порт хранилища результатов анализа. domain/app зависят только на абстракцию."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AnalysisRecord:
    id: int | None
    created_at: datetime | None
    vacancy_text: str
    profile_text: str
    coverage: int
    taxonomy_version: str
    payload_json: str


class AnalysisRepository(Protocol):
    def save(self, record: AnalysisRecord) -> AnalysisRecord:
        """Сохраняет запись, возвращает её же с заполненными id/created_at."""
        ...

    def get(self, record_id: int) -> AnalysisRecord | None: ...

    def list_recent(self, limit: int = 20) -> list[AnalysisRecord]: ...
