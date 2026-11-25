import allure
import pytest
from playwright.sync_api import Page, expect

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
    page.set_viewport_size({"width": width, "height": height})
    lp = LandingPage(page, landing_url)
    lp.open()
    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"Горизонтальный overflow {overflow}px"
    expect(page.locator("h1").first).to_be_visible()