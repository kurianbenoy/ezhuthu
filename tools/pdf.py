#!/usr/bin/env python3
"""Print the HTML specimen to a vector PDF with Chromium.

Requires Playwright + Chromium:
    .venv/bin/pip install playwright
    .venv/bin/python -m playwright install chromium
"""
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "specimen", "index.html")
OUT = os.path.join(ROOT, "proofs", "EzhuthuKamalam-Specimen.pdf")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.goto("file://" + HTML)
        page.wait_for_timeout(3000)  # let fonts load and the bloom finish
        height = page.evaluate("document.documentElement.scrollHeight")
        page.pdf(
            path=OUT,
            width="1600px",
            height=f"{height}px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
