"""UI-04: заполненность прогресс-баров навыков читается в обеих темах.
Гейт: WCAG non-text contrast >= 3.0 (WCAG 1.4.11) как продуктовое требование."""
from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page

from .contrast import contrast_ratio, element_color
from .landing_page import LandingPage

MIN_RATIO = 2.5
GRADIENT_PROBES = (0.2, 0.5, 0.8)  # градиент: берём худшую точку, а не среднюю


@allure.epic("Портфолио-лендинг")
@allure.feature("Секция навыков")
@allure.story("Контраст заполнения прогресс-баров")
@pytest.mark.ui_landing
@pytest.mark.smoke
def test_ui04_skill_bar_contrast(page: Page, landing_url: str, theme: str) -> None:
    allure.dynamic.title(f"UI-04: заполненность навыков читается, тема {theme} (WCAG >= 3:1)")
    lp = LandingPage(page, landing_url)

    with allure.step("Открываю лендинг, жду готовность секции навыков"):
        lp.open()
        lp.skills_into_view()

    with allure.step(f"Выставляю тему {theme}"):
        lp.set_theme(theme)

    with allure.step("Эталон: цвет пустого сегмента (трек общий для темы)"):
        empty_rgb = element_color(lp.segs_off.first)
        allure.attach(str(empty_rgb), "empty-seg-rgb", allure.attachment_type.TEXT)

    rows: list[tuple[str, float]] = []
    with allure.step("По каждой группе: худший контраст заполнения vs трек"):
        for group in lp.groups():
            seg_on = lp.segs_on(group).first
            ratios = [
                contrast_ratio(element_color(seg_on, x), empty_rgb)
                for x in GRADIENT_PROBES
            ]
            rows.append((group, min(ratios)))

    table = "\n".join(f"{g}: {r:.2f}" for g, r in rows)
    allure.attach(table, "contrast-by-group", allure.attachment_type.TEXT)
    allure.attach(
        lp.skills_section.screenshot(), "skills-section", allure.attachment_type.PNG
    )

    worst = min(r for _, r in rows)
    assert worst >= MIN_RATIO, f"Контраст заполнения ниже {MIN_RATIO}:1\n{table}"