import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_text
from .landing_page import LandingPage

FOCUS_JS = """
() => {
  const a = document.activeElement;
  if (!a) return '';
  return a.dataset.testid || a.getAttribute('aria-label') || a.tagName.toLowerCase();
}
"""


@allure.epic("Портфолио-лендинг")
@allure.feature("Доступность")
@allure.story("Клавиатурная навигация до переключателя темы")
@pytest.mark.ui_landing
def test_ui12_keyboard_theme_toggle(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-12: Tab доводит до переключателя темы, Enter переключает")
    allure.dynamic.description(
        "Переключатель темы достижим с клавиатуры не более чем за 15 табов и реагирует на Enter. "
        "Доказательства: число табов, описание сфокусированного элемента, темы до и после."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    focused = ""
    tabs = 0
    with allure.step("Табаюсь до переключателя темы (не более 15 шагов)"):
        for i in range(15):
            page.keyboard.press("Tab")
            tabs = i + 1
            focused = page.evaluate(FOCUS_JS)
            if "theme" in focused.lower() or "тем" in focused.lower():
                break
    reached = "theme" in focused.lower() or "тем" in focused.lower()
    before = lp.current_theme()
    with allure.step("Жму Enter и жду смену темы"):
        if reached:
            page.keyboard.press("Enter")
            page.wait_for_function(
                "b => document.documentElement.classList.contains('dark') !== (b === 'dark')",
                arg=before,
            )
    after = lp.current_theme()
    attach_text("keyboard", f"tabs={tabs} focused={focused} before={before} after={after}")
    assert reached, f"переключатель темы не достижим Tab за 15 шагов, фокус: {focused}"
    assert after != before, "Enter на переключателе не меняет тему"
