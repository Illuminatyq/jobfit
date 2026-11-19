"""SQLAlchemy-адаптер репозитория результатов анализа (Postgres в проде, SQLite в тестах)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from jobfit.logging_config import get_logger
from jobfit.ports.repository import AnalysisRecord


class Base(DeclarativeBase):
    pass


class AnalysisRow(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    vacancy_text: Mapped[str] = mapped_column(Text)
    profile_text: Mapped[str] = mapped_column(Text)
    coverage: Mapped[int] = mapped_column(Integer)
    taxonomy_version: Mapped[str] = mapped_column(String(32))
    payload_json: Mapped[str] = mapped_column(Text)


log = get_logger(__name__)


def make_engine(url: str) -> Engine:
    from sqlalchemy import create_engine

    engine = create_engine(url)
    Base.metadata.create_all(engine)
    log.info("database engine ready for %s", url.split("@")[-1])
    return engine


def _to_record(row: AnalysisRow) -> AnalysisRecord:
    return AnalysisRecord(
        id=row.id,
        created_at=row.created_at,
        vacancy_text=row.vacancy_text,
        profile_text=row.profile_text,
        coverage=row.coverage,
        taxonomy_version=row.taxonomy_version,
        payload_json=row.payload_json,
    )


class SqlAnalysisRepository:
    """Реализация порта AnalysisRepository поверх SQLAlchemy Core/ORM."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, record: AnalysisRecord) -> AnalysisRecord:
        row = AnalysisRow(
            created_at=record.created_at or datetime.now(UTC),
            vacancy_text=record.vacancy_text,
            profile_text=record.profile_text,
            coverage=record.coverage,
            taxonomy_version=record.taxonomy_version,
            payload_json=record.payload_json,
        )
        with Session(self._engine) as session, session.begin():
            session.add(row)
        log.info("saved analysis id=%s coverage=%s", row.id, row.coverage)
        return _to_record(row)

    def get(self, record_id: int) -> AnalysisRecord | None:
        with Session(self._engine) as session:
            row = session.get(AnalysisRow, record_id)
        return _to_record(row) if row else None

    def list_recent(self, limit: int = 20) -> list[AnalysisRecord]:
        stmt = select(AnalysisRow).order_by(AnalysisRow.id.desc()).limit(limit)
        with Session(self._engine) as session:
            rows = list(session.scalars(stmt))
        return [_to_record(r) for r in rows]
