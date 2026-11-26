import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_png, attach_rows
from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Секция навыков")
@allure.story("Фильтрация навыков по группам")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui02_skill_filters(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-02: фильтры навыков переключают группы")
    allure.dynamic.description(
        "Каждая кнопка фильтра оставляет карточки ровно одной группы, "
        "«Все» возвращает полный набор."
    )
    lp = LandingPage(page, landing_url)
    lp.open()
    lp.skills_into_view()
    total = lp.visible_cards.count()
    buttons = lp.filter_buttons
    assert buttons.count() >= 2, "не нашли кнопки фильтров"
    rows: list[list[object]] = []
    with allure.step("Скриншот секции до фильтрации"):
        attach_png(page, "skills-before", locator=lp.skills_section)
    with allure.step("Прохожу по фильтрам, снимаю таблицу кнопка/число/группы"):
        for i in range(1, buttons.count()):
            label = buttons.nth(i).inner_text()
            buttons.nth(i).click()
            page.wait_for_timeout(350)
            visible = lp.visible_cards
            groups = visible.evaluate_all("els => [...new Set(els.map(e => e.dataset.group))]")
            rows.append([label, visible.count(), ", ".join(groups)])
            assert 0 < visible.count() < total
            assert len(groups) == 1, f"фильтр {label} смешал группы: {groups}"
    attach_rows("filters", ["button", "visible", "groups"], rows)
    with allure.step("Скриншот секции после последнего фильтра"):
        attach_png(page, "skills-filtered", locator=lp.skills_section)
    with allure.step("Возвращаю «Все» и проверяю полный набор"):
        buttons.nth(0).click()
        page.wait_for_timeout(350)
        assert lp.visible_cards.count() == total
