import json

import pytest
from fastapi.testclient import TestClient

from jobfit.adapters.db_repository import SqlAnalysisRepository, init_schema, make_engine
from jobfit.entrypoints.api import app
from jobfit.ports.repository import AnalysisRecord


@pytest.fixture()
def engine(tmp_path):  # type: ignore[no-untyped-def]
    eng = make_engine(f"sqlite:///{tmp_path / 'test.db'}")
    init_schema(eng)
    return eng


@pytest.mark.unit
def test_healthz() -> None:
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok"}


@pytest.mark.api
def test_analyze_endpoint_returns_coverage(vacancy_text: str, profile_text: str) -> None:
    client = TestClient(app)
    resp = client.post("/api/analyze", json={"vacancy": vacancy_text, "profile": profile_text})
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["coverage"] <= 100
    assert "critical_gaps" in body


@pytest.mark.api
def test_analyze_rejects_blank_input() -> None:
    client = TestClient(app)
    resp = client.post("/api/analyze", json={"vacancy": "   ", "profile": "x"})
    assert resp.status_code == 422


@pytest.mark.api
def test_save_false_does_not_touch_db(
    monkeypatch: pytest.MonkeyPatch, vacancy_text: str, profile_text: str
) -> None:
    calls: list[int] = []

    def _boom(settings):  # type: ignore[no-untyped-def]
        calls.append(1)
        raise AssertionError("db must not be used when save=False")

    monkeypatch.setattr("jobfit.entrypoints.api._engine_for", _boom)
    client = TestClient(app)
    resp = client.post(
        "/api/analyze", json={"vacancy": vacancy_text, "profile": profile_text, "save": False}
    )
    assert resp.status_code == 200
    assert calls == []


@pytest.mark.unit
def test_repository_roundtrip(engine) -> None:  # type: ignore[no-untyped-def]
    repo = SqlAnalysisRepository(engine)
    saved = repo.save(
        AnalysisRecord(
            id=None,
            created_at=None,
            vacancy_text="Postman",
            profile_text="Postman",
            coverage=100,
            taxonomy_version="v1",
            payload_json=json.dumps({"coverage": 100}),
        )
    )
    assert saved.id is not None and saved.created_at is not None
    fetched = repo.get(saved.id)
    assert fetched is not None
    assert fetched.coverage == 100
    assert [r.id for r in repo.list_recent()] == [saved.id]
