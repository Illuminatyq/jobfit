import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_metrics, attach_offenders, attach_png
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Адаптив")
@allure.story("Отсутствие горизонтального скролла")
@pytest.mark.ui_landing
@pytest.mark.parametrize(
    ("width", "height"),
    [(390, 844), (768, 1024), (1440, 900)],
    ids=["mobile", "tablet", "desktop"],
)
def test_ui06_no_horizontal_scroll(page: Page, landing_url: str, width: int, height: int) -> None:
    allure.dynamic.title(f"UI-06: нет горизонтального скролла на {width}x{height}")
    allure.dynamic.description(
        "Горизонтальный скролл на лендинге ломает мобильный опыт и печать в PDF. "
        "Проверяем, что ни один элемент не вылезает за clientWidth, и фиксируем виновников."
    )
    page.set_viewport_size({"width": width, "height": height})
    allure.dynamic.parameter("viewport", f"{width}x{height}")
    lp = LandingPage(page, landing_url)
    with allure.step("Открываю лендинг"):
        lp.open()
    with allure.step("Снимаю метрики ширины"):
        metrics = attach_metrics(page)
    with allure.step("Ищу элементы за границей viewport"):
        offenders = attach_offenders(page)
    with allure.step("Прикладываю full-page скриншот"):
        attach_png(page, f"fullpage-{width}x{height}", full_page=True)
    with allure.step("Проверяю отсутствие overflow и видимость hero"):
        overflow = metrics["sw"] - metrics["cw"]
        assert overflow <= 0, f"overflow {overflow}px, виновники: {offenders}"
        expect(page.locator("h1").first).to_be_visible()
