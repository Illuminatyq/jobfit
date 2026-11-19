"""Централизованная настройка логирования для всех точек входа jobfit.

Домен (jobfit.domain) остаётся чистым и не импортирует ничего кроме stdlib,
поэтому логгеры ему разрешены, но настраиваются только здесь — на границе
приложения (adapters / entrypoints).
"""

from __future__ import annotations

import logging
import sys

_CONFIGURED_FLAG = "_jobfit_configured"


def setup_logging(level: int | str = logging.INFO, *, stream: object = None) -> logging.Logger:
    """Настраивает корневой логгер jobfit. Идемпотентна: повторные вызовы
    только меняют уровень, дубликаты handler'ов не плодятся."""
    root = logging.getLogger("jobfit")
    if not getattr(root, _CONFIGURED_FLAG, False):
        handler = logging.StreamHandler(stream or sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root.addHandler(handler)
        root.setLevel(level)
        setattr(root, _CONFIGURED_FLAG, True)
    else:
        root.setLevel(level)
    return root


def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер в неймспейсе jobfit.*; при первом обращении
    гарантированно инициализирует базовую конфигурацию."""
    if not name.startswith("jobfit"):
        name = f"jobfit.{name}"
    setup_logging()
    return logging.getLogger(name)
