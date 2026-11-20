# JobFit — контракт для coding-агента
Детерминированный анализ резюме-вакансия + FastAPI-слой. Python 3.11, src-layout, Windows/PowerShell.
Архитектура: domain/app без I/O; adapters — реализации портов; entrypoints тонкие. Персистентность через порт AnalysisRepository (долг: wiring в api.py, рефактор этап 2).
Перед коммитом: pip install -e .[dev]; ruff check .; ruff format .; mypy; pytest -m "not integration and not e2e"; python -m jobfit.entrypoints.eval_cli
Правила: тесты — спецификация; golden.json и пороги не трогать без согласования; type: ignore только с тикетом; FastAPI — Annotated-стиль; ветки + PR, main защищён; не коммитить .env, reports/, venv/, .qwen/; без эмодзи.
Этапы: 0 зелёный CI → 1 Allure+Pages /jobfit/ → 2 БД/Alembic/DI → 3 Docker/GHCR → 4 демо+витрина Astro.
Коммит и пуш только при полностью зелёных локальных гейтах.
Новая ветка только от свежего main после мержа предыдущего PR.
Перед git add -A обязательный git status --short; venv/, data/private/, reports/ в индексе быть не должны.
- При изменении CI/пайплайна или фич JobFit синхронно обновлять портфолио: src/components/CiPipeline.astro (стадии и описания) и карточку JobFit в src/data/cv.ts.