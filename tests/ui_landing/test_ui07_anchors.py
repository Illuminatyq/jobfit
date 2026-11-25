import allure
import pytest
from playwright.sync_api import Page, expect

from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Навигация")
@allure.story("Якорные ссылки скроллят к секциям")
@pytest.mark.ui_landing
def test_ui07_anchor_navigation(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-07: якоря ведут к видимым секциям")
    lp = LandingPage(page, landing_url)
    lp.open()
    links = lp.nav_links
    assert links.count() > 0, "Нет якорных ссылок в шапке"
    for i in range(min(3, links.count())):
        href = links.nth(i).get_attribute("href")
        links.nth(i).click()
        page.wait_for_timeout(450)  # smooth scroll
        expect(page.locator(href)).to_be_in_viewport()
