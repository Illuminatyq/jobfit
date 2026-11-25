import allure
import pytest
from playwright.sync_api import Page, expect


@allure.epic("Портфолио-лендинг")
@allure.feature("404")
@allure.story("Кастомная страница 404 и путь домой")
@pytest.mark.ui_landing
def test_ui09_custom_404(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-09: несуществующий URL отдаёт 404 и ссылку домой")
    resp = page.goto(
        landing_url.rstrip("/") + "/qa-nonexistent-page", wait_until="domcontentloaded"
    )
    assert resp is not None and resp.status == 404
    home = page.locator("a[href='/'], a[href='" + landing_url + "']").first
    expect(home).to_be_visible()
