import allure
import pytest
from playwright.sync_api import Page

from .landing_page import LandingPage


@allure.epic("Портфолио-лендинг")
@allure.feature("Секция навыков")
@allure.story("Фильтрация карточек по категориям")
@pytest.mark.ui_landing
def test_ui02_skill_filters(page: Page, landing_url: str) -> None:
    allure.dynamic.title("UI-02: фильтр показывает только свою группу, «Все» возвращает набор")
    lp = LandingPage(page, landing_url)
    lp.open()
    lp.skills_into_view()
    total = lp.visible_cards.count()
    buttons = lp.filter_buttons
    assert buttons.count() >= 2, "Не нашли кнопки фильтров"
    for i in range(1, buttons.count()):
        buttons.nth(i).click()
        page.wait_for_timeout(350)  # анимация скрытия/показа
        visible = lp.visible_cards
        assert 0 < visible.count() < total
        groups = visible.evaluate_all("els => [...new Set(els.map(e => e.dataset.group))]")
        assert len(groups) == 1, f"Фильтр смешал группы: {groups}"
    buttons.nth(0).click()
    page.wait_for_timeout(350)
    assert lp.visible_cards.count() == total
