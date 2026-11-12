#!/usr/bin/env python3
"""Build a local copy of a dashboard style report page so it can be rendered, checked and turned into a PDF.

  python3 harness.py --page report_page.html --data data_dir --d3 path/to/d3.min.js --out harness.html

The page uses the dashboard runtime: `dash.data(id)`, `dash.calc(id, {inputs, fn})`, `dash.draw(name, fn)`, `dash.colors`, and
the d3 library. This script supplies a stand in for `dash` that reads every <id>.json file of --data and runs every drawing,
so the SAME page code can be tested without the live runtime. A real dashboard still has to judge the page when it is opened.
Get d3 with:  mkdir d3dl && cd d3dl && npm init -y && npm install d3@7.9.0   (file: node_modules/d3/dist/d3.min.js)
"""
import argparse, json, pathlib, re

TOKENS = """:root { --color-fg:#1f2328; --color-fg-muted:#5f6b7a; --color-bg:#ffffff; --color-panel:#f6f7f9; --color-border-line:#dde2e9;
  --color-ok:#1a7f4b; --color-warn:#b7791f; --color-bad:#c0392b; --cds-text-secondary:#4b5563; --cds-chart-grid:#e6e9ee;
  --font-anthropic-sans: Inter, "Helvetica Neue", Arial, sans-serif; --font-anthropic-serif: Georgia, "Times New Roman", serif;
  --cds-font-size-caption:12px; --cds-font-size-body:14px; --cds-gap-sm:8px; --cds-gap-md:12px; --cds-gap-lg:16px; --cds-gap-xl:30px;
  --cds-pad-lg:16px; --cds-radius:8px; --cds-surface-popover:#fff; --cds-border:#cfd6df; --cds-shadow-popover:0 2px 8px rgba(0,0,0,.15); }
body { margin:0; background:var(--color-bg); font-family:var(--font-anthropic-sans); font-size:14px; }
#dash-root { padding: 28px 24px; }
.dash-select { font: inherit; padding: 4px 8px; border:1px solid var(--color-border-line); border-radius:6px; background:var(--color-bg); color:var(--color-fg); }
@media print { section, details, tr { break-inside: avoid; } .sr-tablewrap { overflow: visible; } table { min-width: 0 !important; } }
"""
SHIM = """window.__DATA = %s; window.__calcs = {}; window.__draws = []; window.__errors = [];
window.dash = { colors: ['#2f5fd0', '#d9822b', '#7b5ea7'],
  calc(id, spec) { window.__calcs[id] = spec; },
  data(id) { if (window.__DATA[id]) return { status: 'ok', data: window.__DATA[id] };
    const c = window.__calcs[id];
    if (c) { const ins = c.inputs.map((i) => this.data(i)); if (ins.some((x) => x.status !== 'ok')) return { status: 'missing', data: null };   // like the real runtime: not loaded until every input is
      return { status: 'ok', data: c.fn(...ins.map((x) => x.data)) }; }
    return { status: 'missing', data: [] }; },
  draw(name, fn) { window.__draws.push([name, fn]); } };"""
RUNNER = """window.addEventListener('load', () => { window.__draws.forEach(([name, fn]) => { document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
  try { (typeof fn === 'function' ? fn : fn.update || fn.mount)(el); } catch (e) { window.__errors.push(name + ': ' + e.message); } }); }); window.__done = true; });"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--page", required=True); ap.add_argument("--data", required=True); ap.add_argument("--d3", required=True)
    ap.add_argument("--out", default="harness.html"); ap.add_argument("--tokens", help="CSS file replacing the built in colour and font tokens")
    a = ap.parse_args()
    page = pathlib.Path(a.page).read_text(encoding="utf-8")
    page = re.sub(r'<meta name="dash-one-writer">', "", page)
    m = re.search(r"<script>(.*)</script>", page, re.S)
    if not m: raise SystemExit("the page has no inline <script>")
    markup, script = page[:m.start()], m.group(1)
    data = {p.stem: json.loads(p.read_text()) for p in pathlib.Path(a.data).glob("*.json")}
    tokens = pathlib.Path(a.tokens).read_text() if a.tokens else TOKENS
    d3 = pathlib.Path(a.d3).read_text(encoding="utf-8")
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>Report</title><style>{tokens}</style><script>{d3}</script><script>{SHIM % json.dumps(data)}</script></head>"
            f"<body><div id='dash-root'>{markup}</div><script>{script}</script><script>{RUNNER}</script></body></html>")
    pathlib.Path(a.out).write_text(html, encoding="utf-8")
    print(f"wrote {a.out}: {len(data)} data tables ({', '.join(sorted(data))}), {len(html):,} characters")


if __name__ == "__main__":
    main()
