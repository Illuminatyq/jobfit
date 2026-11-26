import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_png, attach_text
from .landing_page import LandingPage

INTERACTIVE = ["#cp-root", "header nav", "#cp-play"]


@allure.epic("Портфолио-лендинг")
@allure.feature("Печать")
@allure.story("Печатная версия CV")
@pytest.mark.ui_landing
def test_ui10_print_version(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-10: в media print CV читается, интерактив скрыт")
    allure.dynamic.description(
        "Лендинг обещает печать в PDF из браузера. В media print контент CV видим, "
        "а хотя бы один интерактивный блок скрыт. Доказательства: таблица видимости и скриншот."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    with allure.step("Переключаю media в print"):
        page.emulate_media(media="print")
    with allure.step("Снимаю видимость ключевых блоков"):
        states = {sel: page.locator(sel).first.is_visible() for sel in INTERACTIVE}
        cv_visible = page.locator("h1").first.is_visible()
        attach_text(
            "print-visibility",
            " ".join(f"{k}={v}" for k, v in states.items()) + f" cv={cv_visible}",
        )
    with allure.step("Прикладываю full-page скриншот в print"):
        attach_png(page, "fullpage-print", full_page=True)
    with allure.step("Возвращаю media screen"):
        page.emulate_media(media="screen")
    hidden = [sel for sel, visible in states.items() if not visible]
    assert cv_visible, "CV-контент не виден в print"
    assert hidden, f"в print не скрыт ни один интерактивный блок: {states}"
