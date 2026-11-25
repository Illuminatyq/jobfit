import allure
import pytest
from playwright.sync_api import Page, expect

from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Проекты")
@allure.story("Карточка JobFit: ссылки на репо и витрину")
@pytest.mark.ui_landing
def test_ui08_jobfit_links(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-08: ссылки карточки JobFit видимы и живые")
    lp = LandingPage(page, landing_url)
    lp.open()
    repo = page.locator("a[href*='github.com/Illuminatyq/jobfit']").first
    demo = page.locator("a[href*='illuminatyq.github.io/jobfit']").first
    expect(repo).to_be_visible()
    expect(demo).to_be_visible()
    for loc in (repo, demo):
        resp = page.request.get(loc.get_attribute("href"), timeout=15_000)
        assert resp.status < 400
