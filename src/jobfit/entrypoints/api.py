"""HTTP API jobfit. Тонкий слой над use-case analyze; персистентность — через порт."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.engine import Engine

from jobfit.adapters.db_repository import SqlAnalysisRepository, make_engine
from jobfit.adapters.taxonomy_file import load_default_taxonomy
from jobfit.app.analyze import analyze
from jobfit.logging_config import get_logger
from jobfit.ports.repository import AnalysisRecord
from jobfit.settings import Settings

log = get_logger(__name__)


class AnalyzeRequest(BaseModel):
    vacancy: str = Field(min_length=1)
    profile: str = Field(min_length=1)
    save: bool = False


app = FastAPI(title="jobfit", version="0.2.0")

_ENGINES: dict[str, Engine] = {}


def _engine_for(settings: Settings) -> Engine:
    url = settings.database_url
    if url not in _ENGINES:
        _ENGINES[url] = make_engine(url)
    return _ENGINES[url]


def get_settings() -> Settings:
    return Settings()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def api_analyze(
    body: AnalyzeRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    if not body.vacancy.strip() or not body.profile.strip():
        raise HTTPException(status_code=422, detail="vacancy/profile must not be blank")
    result = analyze(body.vacancy, body.profile, load_default_taxonomy())
    payload = asdict(result)
    log.info("api /analyze coverage=%s%% save=%s", result.coverage, body.save)
    if body.save:
        repo = SqlAnalysisRepository(_engine_for(settings))
        record = repo.save(
            AnalysisRecord(
                id=None,
                created_at=None,
                vacancy_text=body.vacancy,
                profile_text=body.profile,
                coverage=result.coverage,
                taxonomy_version=result.taxonomy_version,
                payload_json=json.dumps(payload, ensure_ascii=False),
            )
        )
        payload["id"] = record.id
    return payload


# Статика монтируется ПОСЛЕ всех роутов: catch-all "/" не должен перекрывать
# /healthz, /api/analyze и /docs. Каталог static лежит внутри пакета jobfit.
_STATIC = Path(__file__).resolve().parent.parent / "static"
app.mount("/", StaticFiles(directory=_STATIC, html=True), name="static")
