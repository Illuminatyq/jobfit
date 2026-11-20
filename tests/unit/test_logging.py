"""Регрессия BUG-005: get_logger не сбрасывает уровень логирования."""

import logging
from collections.abc import Iterator

import pytest

from jobfit.logging_config import _CONFIGURED_FLAG, get_logger, setup_logging


@pytest.fixture(autouse=True)
def restore_jobfit_logger() -> Iterator[None]:
    root = logging.getLogger("jobfit")
    saved_handlers = root.handlers[:]
    saved_level = root.level
    saved_flag = getattr(root, _CONFIGURED_FLAG, False)
    yield
    root.handlers = saved_handlers
    root.setLevel(saved_level)
    setattr(root, _CONFIGURED_FLAG, saved_flag)


@pytest.mark.unit
def test_get_logger_does_not_reset_level() -> None:
    setup_logging(level=logging.DEBUG)
    get_logger("jobfit.adapters.example")
    assert logging.getLogger("jobfit").level == logging.DEBUG


@pytest.mark.unit
def test_setup_logging_is_idempotent() -> None:
    setup_logging()
    count = len(logging.getLogger("jobfit").handlers)
    setup_logging()
    assert len(logging.getLogger("jobfit").handlers) == count


@pytest.mark.unit
def test_explicit_level_change_applies() -> None:
    setup_logging(level=logging.DEBUG)
    setup_logging(level="WARNING")
    assert logging.getLogger("jobfit").level == logging.WARNING
