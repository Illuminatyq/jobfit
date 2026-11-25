import re

import allure
import pytest
from playwright.sync_api import expect


@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui01_smoke_main_sections(page, base_url):
    allure.dynamic.title("UI-01 Главная открывается, ключевые секции видимы")
    page.goto(base_url, wait_until="domcontentloaded")
    expect(page).to_have_title(re.compile("QA|Данил", re.IGNORECASE))
    for text in ("Опыт работы", "Проекты", "Навыки", "Связаться"):
        expect(page.get_by_text(text, exact=False).first).to_be_visible()
    assert page.locator("section[id]").count() >= 5