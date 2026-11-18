# JobFit — контекст для coding-агента

## Проект
Детерминированный анализ соответствия резюме вакансии. Публичный QA-портфолио-проект.
Python 3.11, src-layout (src/jobfit), Windows/PowerShell, окружение .venv.
LLM (NVIDIA API, запасной Ollama) — за пределами MVP, в ядро не добавлять.

## Архитектура (порты и адаптеры)
- domain/ — чистая логика без I/O: extract, normalize, scoring, taxonomy, model, hints
- app/analyze.py — use case; adapters/ — файловые реализации
- entrypoints/ — cli.py, eval_cli.py
- eval/ — dataset, metrics, runner; датасет eval/golden.json (8 gate-кейсов G01-G08, 2 known gap K01-K02)
- Детерминизм обязателен: один вход — один выход, без сети и случайности.

## Команды качества (перед любым коммитом, все зелёные)
ruff check .
ruff format .
mypy
pytest --cov --cov-report=term-missing
python -m jobfit.entrypoints.eval_cli

## Жёсткие правила
- Пороги eval-гейтов не ослаблять, golden.json не менять без согласования.
- Нет датасета — красный тест, не skip.
- Known gap закрывается только переводом кейса в gate.
- Не коммитить: .env, reports/, venv/, .venv/, data/private/. Секреты только через env.
- Работа в ветках feat/*, в main напрямую не пушить.
- Каждый баг: docs/bugs/BUG-NNN.md + регрессионный тест. Без эмодзи.

## Бэклог (приоритет сверху)
1. Тесты entrypoints/eval_cli.py (сейчас 0% покрытия).
2. runpy-warning в test_cli.py::test_module_entrypoint.
3. Покрыть runner.py (строки 111-115, 134-164, 168-172).
4. Закрыть K01 (MySQL подразумевает SQL) и K02 (порядок слов REST API), перевести в gate.
5. Усложнить golden: все gate-кейсы сейчас F1=1.0, нужны адверсариальные.
6. README: бейдж CI, описание гейтов.