"""Integration: репозиторий против реального Postgres. Схема создана alembic upgrade head в CI."""

import json
import os

import pytest

from jobfit.adapters.db_repository import SqlAnalysisRepository, make_engine
from jobfit.ports.repository import AnalysisRecord

pytestmark = pytest.mark.integration


@pytest.fixture()
def pg_engine():  # type: ignore[no-untyped-def]
    url = os.environ.get("JOBFIT_DATABASE_URL", "")
    if not url.startswith("postgresql"):
        pytest.skip("JOBFIT_DATABASE_URL not pointed at Postgres")
    return make_engine(url)


def test_postgres_roundtrip(pg_engine) -> None:  # type: ignore[no-untyped-def]
    repo = SqlAnalysisRepository(pg_engine)
    saved = repo.save(
        AnalysisRecord(
            id=None,
            created_at=None,
            vacancy_text="Senior QA",
            profile_text="QA engineer",
            coverage=80,
            taxonomy_version="1.0.0",
            payload_json=json.dumps({"coverage": 80}),
        )
    )
    assert saved.id is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.coverage == 80
    assert any(r.id == saved.id for r in repo.list_recent())
