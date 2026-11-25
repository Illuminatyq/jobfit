"""Пиксельный контраст по WCAG 2.x. Меряем отрендеренный цвет, а не computed-фон:
у .seg.on фон — градиент, backgroundColor вернул бы transparent."""
from __future__ import annotations

import io
import statistics

from PIL import Image
from playwright.sync_api import Locator


def _to_linear(channel: int) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def element_color(loc: Locator, x_frac: float = 0.5) -> tuple[int, int, int]:
    """Медианный RGB в вертикальном срезе элемента на позиции x_frac по ширине.
    Центр по высоте inset-бордер 1px."""
    loc.scroll_into_view_if_needed()
    handle = loc.element_handle()
    # opacityreveal живёт на article-предке, у самого span computed opacity = 1.
    loc.page.wait_for_function(
        "el => getComputedStyle(el.closest('article') ?? el).opacity === '1'",
        arg=handle,
    )
    img = Image.open(io.BytesIO(loc.screenshot())).convert("RGB")
    w, h = img.size
    x = min(w - 1, max(0, int(w * x_frac)))
    ys = range(max(0, h // 2 - 1), min(h, h // 2 + 2))
    pixels = [img.getpixel((x, y)) for y in ys]
    return tuple(int(statistics.median(p[i] for p in pixels)) for i in range(3))