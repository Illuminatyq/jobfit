FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md* alembic.ini ./
COPY migrations ./migrations
COPY src ./src
RUN pip install --upgrade pip && pip install .

EXPOSE 8000

HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn jobfit.entrypoints.api:app --host 0.0.0.0 --port ${PORT:-8000}"]