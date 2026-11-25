"""Фикстуры UI-тестов лендинга. Чёрный ящик против LANDING_URL (прод или превью)."""
from __future__ import annotations

import os

import allure
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def landing_url() -> str:
    return os.getenv("LANDING_URL", "https://illuminatyq.github.io/")


@pytest.fixture(scope="session")
def base_url(landing_url: str) -> str:
    # Для плагина pytest-playwright и твоего test_smoke.py (UI-01).
    return landing_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    args = {**browser_context_args, "viewport": {"width": 1440, "height": 900}}
    proxy = os.getenv("UI_PROXY")
    if proxy:
        args["proxy"] = {"server": proxy}
    return args


@pytest.fixture()
def page(page: Page) -> Page:
    page.set_default_timeout(15_000)
    page.set_default_navigation_timeout(30_000)
    return page


@pytest.fixture(params=["light", "dark"], ids=["light", "dark"])
def theme(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(autouse=True)
def _allure_ui_group(browser_name: str) -> None:
    # Корневой conftest ставит unit/integration, группу ui-landing ставим здесь.
    allure.dynamic.parent_suite("ui-landing")
    allure.dynamic.suite(browser_name)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        pg: Page | None = item.funcargs.get("page")
        if pg is not None:
            try:
                allure.attach(
                    pg.screenshot(full_page=True),
                    "screenshot-on-fail",
                    allure.attachment_type.PNG,
                )
                allure.attach(pg.url, "page-url", allure.attachment_type.TEXT)
            except Exception:
                pass  # страница могла быть закрыта — не валим отчёт