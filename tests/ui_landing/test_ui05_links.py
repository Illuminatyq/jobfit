import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_png, attach_rows
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Ссылки")
@allure.story("Живость ключевых ссылок")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui05_key_links_alive(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-05: GitHub и PDF отдают 2xx/3xx, mailto присутствует")
    allure.dynamic.description(
        "Все внешние ссылки на GitHub и PDF живые, mailto на месте. "
        "Доказательства: таблица url/status/content-type и скриншот блока контактов."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    hrefs = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
    targets = sorted(
        {h for h in hrefs if h.startswith("http") and ("github.com" in h or h.endswith(".pdf"))}
    )
    assert targets, "не нашли ссылок на GitHub/PDF"
    rows: list[list[object]] = []
    with allure.step("Обхожу внешние ссылки и снимаю таблицу"):
        for href in targets:
            resp = page.request.get(href, timeout=15_000)
            rows.append([href, resp.status, resp.headers.get("content-type", "")])
            assert resp.status < 400, f"{href} -> {resp.status}"
    attach_rows("links", ["url", "status", "content-type"], rows)
    with allure.step("Скриншот блока контактов"):
        attach_png(page, "contacts", locator=page.locator("section:has(a[href^='mailto:'])").first)
    with allure.step("Проверяю наличие mailto"):
        assert any(h.startswith("mailto:") for h in hrefs), "нет mailto-ссылки"
