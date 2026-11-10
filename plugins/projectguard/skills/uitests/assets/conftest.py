"""Shared fixtures for browser (Playwright) tests. Copy to tests/conftest.py and adjust PAGE."""
import os, pathlib, pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = (ROOT / "dist" / "app.html").as_uri()          # FILL IN: the built page the users really open


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        # PQ_CHROMIUM=/path/to/chromium uses an existing browser. Needed when the installed Playwright expects a different
        # browser build than the one on the machine ("Executable doesn't exist"); has no effect when unset.
        exe = os.environ.get("PQ_CHROMIUM")
        b = p.chromium.launch(executable_path=exe, args=["--no-sandbox"]) if exe else p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def open_page(browser):
    """open_page(locale='en-US', width=1366) -> (page, errors). `errors` collects uncaught page errors: assert it is empty."""
    made = []

    def _open(locale="en-US", width=1366):
        ctx = browser.new_context(viewport={"width": width, "height": 900}, locale=locale, accept_downloads=True)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(PAGE)
        pg.wait_for_timeout(400)
        made.append(ctx)
        return pg, errs

    yield _open
    for c in made:
        c.close()


@pytest.fixture
def page(open_page):
    pg, errs = open_page()
    pg.on("dialog", lambda d: d.dismiss())             # alert and confirm boxes would otherwise hang the test
    yield pg
    assert not errs, errs
