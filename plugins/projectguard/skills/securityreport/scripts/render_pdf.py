#!/usr/bin/env python3
"""Render a harness page in a real browser: check it, take screenshots, and write a PDF.

  python3 render_pdf.py harness.html --pdf report.pdf [--shot full.png] [--width 940] [--scale 0.8] [--hide .controls] [--title "My report"]

Checks printed (exit code 1 if any fails): drawing errors, console errors, drawings still showing the placeholder dash,
and sideways overflow. Then the PDF: A4, backgrounds on, page numbers in the footer, interactive controls hidden (--hide),
all <details> opened. Browser: set PQ_CHROMIUM=/path/to/chromium to use an existing one (see the uitests skill).
A PDF made this way is a SNAPSHOT of the data it was given; the live page is the one to keep updating.
"""
import argparse, os, pathlib, sys
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("harness"); ap.add_argument("--pdf"); ap.add_argument("--shot"); ap.add_argument("--width", type=int, default=940)
    ap.add_argument("--scale", type=float, default=0.8); ap.add_argument("--hide", action="append", default=[]); ap.add_argument("--title", default="Report")
    a = ap.parse_args(); bad = 0
    with sync_playwright() as p:
        exe = os.environ.get("PQ_CHROMIUM")
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"]) if exe else p.chromium.launch()
        pg = b.new_context(viewport={"width": a.width, "height": 1200}).new_page(); logs = []
        pg.on("console", lambda m: logs.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: logs.append(str(e)))
        pg.goto(pathlib.Path(a.harness).resolve().as_uri()); pg.wait_for_function("window.__done === true", timeout=30000); pg.wait_for_timeout(400)
        errors = pg.evaluate("window.__errors"); empty = pg.evaluate("[...document.querySelectorAll('[data-draw]')].filter(e => e.textContent.trim() === '—').map(e => e.dataset.draw)")
        over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        for label, bad_cond, text in (("drawing errors", errors, errors), ("console errors", logs, logs[:3]), ("drawings still showing the placeholder", empty, empty), ("sideways overflow", over > 0, over)):
            print(("FAIL " if bad_cond else "ok   ") + label + (f": {text}" if bad_cond else "")); bad += 1 if bad_cond else 0
        if a.shot: pg.screenshot(path=a.shot, full_page=True); print("screenshot", a.shot)
        if a.pdf:
            hide = ", ".join(a.hide)
            pg.add_style_tag(content="@media print { " + (hide + " { display: none !important; } " if hide else "") + "#dash-root { padding: 0 !important; } }")
            pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)"); pg.emulate_media(media="print")
            pg.pdf(path=a.pdf, format="A4", print_background=True, scale=a.scale, margin={"top": "12mm", "bottom": "16mm", "left": "11mm", "right": "11mm"}, display_header_footer=True,
                   header_template="<span></span>", footer_template=f'<div style="font-size:8px;width:100%;text-align:center;color:#5f6b7a;font-family:Arial">{a.title}. Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>')
            print("pdf", a.pdf)
        b.close()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
