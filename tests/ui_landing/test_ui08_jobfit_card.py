import allure
import pytest
from playwright.sync_api import Page, expect

from .attachments import attach_png, attach_rows
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Проекты")
@allure.story("Карточка JobFit: ссылки на репо и витрину")
@pytest.mark.ui_landing
def test_ui08_jobfit_links(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-08: ссылки карточки JobFit видимы и живые")
    allure.dynamic.description(
        "Карточка JobFit содержит рабочие ссылки на репозиторий и витрину отчёта. "
        "Доказательства: таблица href/status и скриншот карточки."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    repo = page.locator("a[href*='github.com/Illuminatyq/jobfit']").first
    demo = page.locator("a[href*='illuminatyq.github.io/jobfit']").first
    with allure.step("Проверяю видимость обеих ссылок"):
        expect(repo).to_be_visible()
        expect(demo).to_be_visible()
    rows: list[list[object]] = []
    with allure.step("Обхожу ссылки и снимаю статусы"):
        for loc in (repo, demo):
            href = loc.get_attribute("href") or ""
            resp = page.request.get(href, timeout=15_000)
            rows.append([href, resp.status])
            assert resp.status < 400, f"{href} -> {resp.status}"
    attach_rows("jobfit-links", ["href", "status"], rows)
    with allure.step("Скриншот секции проектов"):
        attach_png(
            page,
            "jobfit-card",
            locator=page.locator("section:has(a[href*='github.com/Illuminatyq/jobfit'])").first,
        )
