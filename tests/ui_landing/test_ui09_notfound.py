import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_png, attach_text


@allure.epic("Портфолио-лендинг")
@allure.feature("404")
@allure.story("Кастомная страница 404 и путь домой")
@pytest.mark.ui_landing
def test_ui09_custom_404(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-09: несуществующий URL отдаёт 404 и ссылку домой")
    allure.dynamic.description(
        "Несуществующий адрес отдаёт статус 404 и понятную страницу с путём домой. "
        "Доказательства: статус, итоговый url и full-page скриншот."
    )
    with allure.step("Открываю несуществующий адрес"):
        resp = page.goto(
            landing_url.rstrip("/") + "/qa-nonexistent-page", wait_until="domcontentloaded"
        )
    with allure.step("Фиксирую статус и url"):
        status = resp.status if resp is not None else -1
        attach_text("404-meta", f"status={status} url={page.url}")
    with allure.step("Прикладываю full-page скриншот"):
        attach_png(page, "page-404", full_page=True)
    with allure.step("Проверяю статус и ссылку домой"):
        assert status == 404
        home = page.locator("a[href='/'], a[href='" + landing_url + "']").first
        expect(home).to_be_visible()
