import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_png, attach_text


@allure.epic("Портфолио-лендинг")
@allure.feature("Печать")
@allure.story("Кнопка 'Сохранить CV в PDF' вызывает печать")
@pytest.mark.ui_landing
def test_ui14_print_cv_button(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-14: кнопка 'Сохранить CV в PDF' видима и вызывает window.print")
    allure.dynamic.description(
        "Кнопка печати видима, кликабельна, и при клике вызывает window.print(). "
        "Доказательства: скриншот кнопки, её атрибуты, флаг вызова print."
    )
    with allure.step("Открываю лендинг"):
        page.goto(landing_url, wait_until="domcontentloaded")
        expect(page.locator("h1").first).to_be_visible()
    with allure.step("Нахожу кнопку печати"):
        btn = (
            page.locator("#print-cv")
            .or_(page.get_by_role("button", name="Сохранить CV в PDF"))
            .first
        )
        expect(btn).to_be_visible()
        tag = btn.evaluate("el => el.tagName")
        attach_text("print-button", f"tag={tag} id={btn.get_attribute('id')}")
        attach_png(page, "print-button-visible", locator=btn)
    with allure.step("Перехватываю window.print и кликаю"):
        page.evaluate(
            "window.__printCalled = false; window.print = () => { window.__printCalled = true; }"
        )
        btn.click()
        page.wait_for_timeout(300)
    with allure.step("Проверяю, что window.print был вызван"):
        called = page.evaluate("window.__printCalled")
        attach_text("print-call", f"window.print called: {called}")
    assert called, "кнопка не вызвала window.print()"
