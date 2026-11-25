"""Page Object лендинга. Селекторы — на семантических классах и ролях."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect


class LandingPage:
    def __init__(self, page: Page, url: str) -> None:
        self.page = page
        self.url = url

    @property
    def skill_cards(self) -> Locator:
        return self.page.locator("article.skill-item")

    @property
    def visible_cards(self) -> Locator:
        return self.page.locator("article.skill-item:visible")

    @property
    def skills_section(self) -> Locator:
        return self.page.locator("section").filter(has=self.skill_cards).first

    @property
    def filter_buttons(self) -> Locator:
        return self.skills_section.get_by_role("button")

    def segs_on(self, group: str) -> Locator:
        return self.page.locator(f"article.skill-item[data-group='{group}'] .seg.on")

    @property
    def segs_off(self) -> Locator:
        return self.page.locator("article.skill-item .seg:not(.on)")

    @property
    def theme_toggle(self) -> Locator:
        return (
            self.page.get_by_test_id("theme-toggle")
            .or_(
                self.page.locator(
                    "button[aria-label*='theme' i], button[aria-label*='тем' i],"
                    " button[title*='theme' i], button[title*='тем' i]"
                )
            )
            .first
        )

    @property
    def nav_links(self) -> Locator:
        return self.page.locator("header a[href^='#'], nav a[href^='#']")

    def open(self) -> None:
        self.page.goto(self.url, wait_until="domcontentloaded")
        expect(self.page.locator("h1").first).to_be_visible()

    def current_theme(self) -> str:
        dark = self.page.evaluate("document.documentElement.classList.contains('dark')")
        return "dark" if dark else "light"

    def set_theme(self, theme: str) -> None:
        # Предусловие рендер-теста: класс темы напрямую, без клика.
        # Механику кнопки и persistence проверяет UI-03.
        self.page.evaluate(
            "t => document.documentElement.classList.toggle('dark', t === 'dark')",
            theme,
        )
        self.page.wait_for_function(
            "t => document.documentElement.classList.contains('dark') === (t === 'dark')",
            arg=theme,
        )

    def skills_into_view(self) -> None:
        self.skill_cards.first.scroll_into_view_if_needed()
        self.skill_cards.last.scroll_into_view_if_needed()
        self.page.mouse.move(0, 0)
        expect(self.skill_cards.first).to_have_css("opacity", "1")
        expect(self.skill_cards.last).to_have_css("opacity", "1")

    def groups(self) -> list[str]:
        return self.skill_cards.evaluate_all("els => [...new Set(els.map(e => e.dataset.group))]")
