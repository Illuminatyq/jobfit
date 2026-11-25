import allure
import pytest
from playwright.sync_api import Page

from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Тема оформления")
@allure.story("Переключение и сохранение темы")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui03_theme_toggle_persistence(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-03: тема переключается и сохраняется после reload")
    lp = LandingPage(page, landing_url)
    lp.open()
    if lp.theme_toggle.count() == 0:
        pytest.skip("Нет testid/aria-label у кнопки темы: нужен micro-PR лендинга")
    before = lp.current_theme()
    lp.theme_toggle.click()
    page.wait_for_function(
        "b => document.documentElement.classList.contains('dark') !== (b === 'dark')",
        arg=before,
    )
    after = lp.current_theme()
    assert after != before
    page.reload(wait_until="domcontentloaded")
    assert lp.current_theme() == after, "Тема не сохранилась после reload"