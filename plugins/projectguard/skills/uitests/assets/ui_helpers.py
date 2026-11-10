"""Helpers for the traps that make browser tests flaky or silently empty. Import what you need."""
import pathlib, re


def screen_point(page, svg_selector, view_x, view_y):
    """Convert a point in an SVG drawing's own coordinates (viewBox units) to a position on the screen.
    Scrolls the drawing into view FIRST: clicking a button can scroll the page and push the drawing off screen, and a mouse
    action at an off screen position lands on nothing, silently."""
    page.locator(svg_selector).scroll_into_view_if_needed()
    page.wait_for_timeout(150)
    return page.evaluate("""([sel, vx, vy]) => { const s = document.querySelector(sel), p = s.createSVGPoint();
        p.x = vx; p.y = vy; const r = p.matrixTransform(s.getScreenCTM()); return [r.x, r.y]; }""", [svg_selector, view_x, view_y])


def drag(page, svg_selector, a, b):
    (x1, y1), (x2, y2) = screen_point(page, svg_selector, *a), screen_point(page, svg_selector, *b)
    page.mouse.move(x1, y1)
    page.mouse.down()
    page.mouse.move((x1 + x2) / 2, (y1 + y2) / 2, steps=4)
    page.mouse.move(x2, y2, steps=4)
    page.mouse.up()
    page.wait_for_timeout(200)


def ctrl_wheel(page, svg_selector, vx, vy, delta, ctrl=True):
    """Dispatch a wheel event directly: deterministic, unlike a real wheel plus held key."""
    x, y = screen_point(page, svg_selector, vx, vy)
    page.evaluate("""([sel, x, y, d, c]) => document.querySelector(sel).dispatchEvent(
        new WheelEvent('wheel', {clientX: x, clientY: y, deltaY: d, ctrlKey: c, bubbles: true, cancelable: true}))""", [svg_selector, x, y, delta, ctrl])
    page.wait_for_timeout(150)


def open_collapsed_section(page, selector):
    """Controls inside a closed <details> are not visible, so a click times out with 'element is not visible'."""
    page.evaluate("(sel) => { const d = document.querySelector(sel).closest('details'); if (d) d.open = true; }", selector)


def stub_print(page, works=True):
    """A headless browser has no printer. works=True announces 'printing started' (the page keeps its print sheet);
    works=False does nothing (the page should offer its fallback, for example a PDF)."""
    page.evaluate("window.print = () => window.dispatchEvent(new Event('beforeprint'))" if works else "window.print = () => {}")


def pdf_facts(path):
    """Structure of a PDF file without a PDF library. Page text is compressed, so test STRUCTURE, not wording."""
    data = pathlib.Path(path).read_bytes()
    title = re.search(rb"/Title \(([^)]*)\)", data)
    return {"bytes": len(data), "starts": data[:5], "ends": data.rstrip()[-5:],
            "pages": max([int(n) for n in re.findall(rb"/Count (\d+)", data)] or [0]),
            "title": title.group(1).decode() if title else None, "images": data.count(b"/Subtype /Image")}


def close_to_shown_digits(shown, saved, significant=3):
    """A report shows `significant` digits of the true value while a file keeps more. Two roundings can disagree exactly at a
    rounding edge (39.05 -> 39.1 versus 39.0), so compare with the rounding step as tolerance, never with equality."""
    return abs(float(shown) - float(saved)) <= (0.5 * 10 ** (1 - significant)) * 1.2 * abs(float(saved))
