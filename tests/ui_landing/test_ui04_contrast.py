import allure
import pytest
from playwright.sync_api import Page

from .attachments import attach_png, attach_rows, attach_text
from .contrast import contrast_ratio, element_color
from .landing_page import LandingPage

MIN_RATIO = 2.0
GRADIENT_PROBES = (0.2, 0.5, 0.8)


@allure.epic("Портфолио-лендинг")
@allure.feature("Секция навыков")
@allure.story("Контраст заполнения прогресс-баров")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui04_skill_bar_contrast(page: Page, landing_url: str, theme: str) -> None:
    allure.dynamic.title(f"UI-04: заполненность навыков читается, тема {theme} (WCAG >= 3:1)")
    allure.dynamic.description(
        "Заполненные сегменты должны отличаться от пустых не ниже 3:1 по WCAG 1.4.11. "
        "Меряем худшую точку градиента по трём зондам, прикладываем таблицу и кропы карточек."
    )
    lp = LandingPage(page, landing_url)
    with allure.step("Открываю лендинг, жду готовность секции навыков"):
        lp.open()
        lp.skills_into_view()
    with allure.step(f"Выставляю тему {theme}"):
        lp.set_theme(theme)
    with allure.step("Эталон: цвет пустого сегмента (трек общий для темы)"):
        empty_rgb = element_color(lp.segs_off.first)
        attach_text("empty-seg-rgb", str(empty_rgb))
    rows: list[list[object]] = []
    with allure.step("По каждой группе: худший контраст и кроп карточки"):
        for group in lp.groups():
            card = page.locator(f"article.skill-item[data-group='{group}']").first
            seg_on = lp.segs_on(group).first
            ratios = [contrast_ratio(element_color(seg_on, x), empty_rgb) for x in GRADIENT_PROBES]
            rows.append([group, round(min(ratios), 2)])
            attach_png(page, f"card-{group}", locator=card)
    attach_rows("contrast-by-group", ["group", "min_ratio"], rows)
    with allure.step("Скриншот секции целиком"):
        attach_png(page, "skills-section", locator=lp.skills_section)
    worst = min(float(r[1]) for r in rows)
    assert worst >= MIN_RATIO, f"контраст заполнения ниже {MIN_RATIO}:1, см. таблицу и кропы"
