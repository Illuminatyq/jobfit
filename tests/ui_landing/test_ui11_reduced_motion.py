import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_text
from .landing_page import LandingPage

LAYERS_JS = """
() => ['.aurora', '.spotlight', '.grain'].map((s) => {
  const el = document.querySelector(s);
  if (!el) return { sel: s, name: 'absent', dur: '0s' };
  const c = getComputedStyle(el);
  return { sel: s, name: c.animationName, dur: c.animationDuration };
})
"""


@allure.epic("Портфолио-лендинг")
@allure.feature("Анимации")
@allure.story("Уважение prefers-reduced-motion")
@pytest.mark.ui_landing
def test_ui11_reduced_motion(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-11: фоновые анимации отключаются при reduced motion")
    allure.dynamic.description(
        "При prefers-reduced-motion: reduce фоновые слои не анимируются. "
        "Доказательства: computed animation-duration."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    with allure.step("Эмулирую prefers-reduced-motion: reduce"):
        page.emulate_media(reduced_motion="reduce")
    with allure.step("Снимаю computed animation фоновых слоёв"):
        layers = page.evaluate(
            "() => ['.aurora', '.spotlight', '.grain'].map(sel => {"
            "const el = document.querySelector(sel);"
            "if (!el) return { sel, name: 'absent', dur: '0s' };"
            "const c = getComputedStyle(el);"
            "return { sel, name: c.animationName, dur: c.animationDuration };"
            "})"
        )
        attach_text(
            "reduced-motion",
            "\n".join(f"{layer['sel']}: {layer['name']} {layer['dur']}" for layer in layers),
        )
    with allure.step("Возвращаю no-preference"):
        page.emulate_media(reduced_motion="no-preference")
    running = [
        layer
        for layer in layers
        if layer["name"] not in ("none", "absent") and layer["dur"] not in ("0s", "")
    ]
    assert not running, f"анимации не остановлены при reduced motion: {running}"
