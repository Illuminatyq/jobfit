"""Вложения-доказательства для Allure: скриншоты, таблицы, метрики, виновники overflow."""

from __future__ import annotations

import csv
import io

import allure
from playwright.sync_api import Locator, Page

OFFENDERS_JS = """
() => {
  const cw = document.documentElement.clientWidth;
  const out = [];
  document.querySelectorAll('*').forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.right > cw + 1 && r.width > 0) {
      const cls = (el.className || '').toString().split(' ').slice(0, 3).join('.');
      out.push(el.tagName.toLowerCase() + '.' + cls + ' right=' + Math.round(r.right));
    }
  });
  return out.slice(0, 20);
}
"""


def attach_png(
    page: Page, name: str, locator: Locator | None = None, full_page: bool = False
) -> None:
    shot = locator.screenshot() if locator is not None else page.screenshot(full_page=full_page)
    allure.attach(shot, name, allure.attachment_type.PNG)


def attach_text(name: str, content: str) -> None:
    allure.attach(content, name, allure.attachment_type.TEXT)


def attach_rows(name: str, header: list[str], rows: list[list[object]]) -> None:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    allure.attach(buf.getvalue(), name, allure.attachment_type.CSV)


def attach_offenders(page: Page, name: str = "overflow-offenders") -> list[str]:
    offenders = page.evaluate(OFFENDERS_JS)
    attach_text(name, "\n".join(offenders) if offenders else "элементов за границей viewport нет")
    return offenders


def attach_metrics(page: Page, name: str = "viewport-metrics") -> dict[str, int]:
    m = page.evaluate(
        "() => ({sw: document.documentElement.scrollWidth,"
        " cw: document.documentElement.clientWidth, iw: window.innerWidth})"
    )
    attach_text(name, f"scrollWidth={m['sw']} clientWidth={m['cw']} innerWidth={m['iw']}")
    return m
