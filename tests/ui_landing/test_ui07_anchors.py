import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_png, attach_text
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Навигация")
@allure.story("Якорные ссылки скроллят к секциям")
@pytest.mark.ui_landing
def test_ui07_anchor_navigation(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-07: якоря ведут к видимым секциям")
    allure.dynamic.description(
        "Клик по якорю доводит целевую секцию до viewport. "
        "Доказательства: координата y цели и скриншот после каждого клика."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    links = lp.nav_links
    assert links.count() > 0, "нет якорных ссылок в шапке"
    with allure.step("Прохожу по первым трём якорям"):
        for i in range(min(3, links.count())):
            href = links.nth(i).get_attribute("href") or ""
            links.nth(i).click()
            page.wait_for_timeout(450)
            target = page.locator(href)
            box = target.bounding_box()
            attach_text(f"anchor-{href}", f"y={round(box['y']) if box else -1}")
            attach_png(page, f"after-click-{href.strip('#')}")
            expect(target).to_be_in_viewport()
