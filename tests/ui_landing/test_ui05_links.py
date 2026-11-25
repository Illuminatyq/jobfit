import allure
import pytest
from playwright.sync_api import Page

from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Ссылки")
@allure.story("Живость ключевых ссылок")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui05_key_links_alive(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-05: GitHub и PDF резюме отдают 2xx/3xx, mailto присутствует")
    lp = LandingPage(page, landing_url)
    lp.open()
    hrefs = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
    targets = sorted(
        {h for h in hrefs if h.startswith("http") and ("github.com" in h or h.endswith(".pdf"))}
    )
    assert targets, "Не нашли ссылок на GitHub/PDF"
    for href in targets:
        resp = page.request.get(href, timeout=15_000)
        assert resp.status < 400, f"{href} -> {resp.status}"
    assert any(h.startswith("mailto:") for h in hrefs), "Нет mailto-ссылки"
