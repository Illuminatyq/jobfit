import os

import pytest
from fastapi.testclient import TestClient

from jobfit.adapters.db_repository import SqlAnalysisRepository, make_engine
from jobfit.entrypoints.api import app


@pytest.fixture(scope="module")
def db_url() -> str:
    url = os.environ.get("JOBFIT_DATABASE_URL")
    if not url:
        pytest.skip("set JOBFIT_DATABASE_URL to run integration tests against real Postgres")
    return url


@pytest.mark.integration
def test_save_persists_in_postgres(db_url: str, vacancy_text: str, profile_text: str) -> None:
    engine = make_engine(db_url)
    repo = SqlAnalysisRepository(engine)
    before = len(repo.list_recent(limit=100))

    client = TestClient(app)
    resp = client.post(
        "/api/analyze", json={"vacancy": vacancy_text, "profile": profile_text, "save": True}
    )
    assert resp.status_code == 200
    record_id = resp.json()["id"]
    assert record_id is not None

    after = len(repo.list_recent(limit=100))
    assert after == before + 1
    stored = repo.get(record_id)
    assert stored is not None
    assert stored.vacancy_text == vacancy_text
