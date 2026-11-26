"""Фикстуры UI-тестов лендинга: контекст, тема, консоль, параметры Allure."""

from __future__ import annotations

import os
from collections.abc import Iterator

import allure
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def landing_url() -> str:
    return os.getenv("LANDING_URL", "https://illuminatyq.github.io/")


@pytest.fixture(scope="session")
def base_url(landing_url: str) -> str:
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
    allure.dynamic.parameter("theme", request.param)
    return request.param


@pytest.fixture(autouse=True)
def _console_capture(page: Page) -> Iterator[list[str]]:
    logs: list[str] = []
    page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
    page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
    yield logs


@pytest.fixture(autouse=True)
def _allure_context(page: Page, browser_name: str) -> None:
    allure.dynamic.parent_suite("ui-landing")
    allure.dynamic.suite(browser_name)
    allure.dynamic.parameter("browser", browser_name)
    vp = page.viewport_size or {}
    allure.dynamic.parameter("viewport", f"{vp.get('width')}x{vp.get('height')}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page: Page | None = item.funcargs.get("page")
        if page is None:
            return
        try:
            allure.attach(
                page.screenshot(full_page=True),
                "screenshot-on-fail",
                allure.attachment_type.PNG,
            )
            allure.attach(page.url, "page-url", allure.attachment_type.TEXT)
            logs: list[str] = item.funcargs.get("_console_capture") or []
            if logs:
                allure.attach(
                    "\n".join(logs[-50:]),
                    "console-last-50",
                    allure.attachment_type.TEXT,
                )
            allure.attach(page.content(), "dom-on-fail", allure.attachment_type.HTML)
        except Exception:
            pass
