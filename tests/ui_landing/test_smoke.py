import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_png, attach_text
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Smoke")
@allure.story("Главная открывается, ключевые секции видимы")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui01_smoke_main_sections(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-01: главная открывается, ключевые секции видимы")
    allure.dynamic.description(
        "Базовый smoke: страница отдаётся, hero и секции на месте. "
        "Доказательства: статус, время до DOMContentLoaded, список секций, скриншот."
    )
    lp = LandingPage(page, landing_url)
    with allure.step("Открываю лендинг"):
        lp.open()
    with allure.step("Фиксирую статус и время загрузки"):
        attach_text("load", f"status={lp.status} dom_ready_ms={lp.dom_ready_ms()}")
    with allure.step("Снимаю список видимых секций"):
        ids = lp.visible_section_ids()
        attach_text("visible-sections", ", ".join(ids))
    with allure.step("Прикладываю full-page скриншот"):
        attach_png(page, "fullpage-smoke", full_page=True)
    with allure.step("Проверяю статус, секции и hero"):
        assert lp.status == 200
        assert ids, "не нашлось ни одной видимой секции с id"
        expect(page.locator("h1").first).to_be_visible()
