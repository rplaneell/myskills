#!/usr/bin/env python3
"""Pull the inline <script> blocks out of a built HTML page into .js files, so a code scanner can read them.

Why: a single file web tool keeps all its JavaScript inside one HTML file, and scanners read .js files.
Vendored libraries (code you copied in unchanged) are skipped because they are not your code: point --vendor-dir at the
folder holding the original library files, and any script that starts with the same first 300 characters is skipped.

  python3 extract_inline_scripts.py dist/app.html semgrep_input [--vendor-dir src/vendor] [--max-chars 0]
--max-chars N  also skip scripts longer than N characters (0 = off), a fallback when you have no vendor folder.
"""
import argparse, pathlib, re, sys


def extract(html_path, out_dir, vendor_dirs=(), max_chars=0):
    html = pathlib.Path(html_path).read_text(encoding="utf-8")
    heads = [p.read_text(encoding="utf-8").strip()[:300] for d in vendor_dirs for p in sorted(pathlib.Path(d).glob("*.js"))]
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.js"):
        old.unlink()
    kept = skipped = 0
    for i, m in enumerate(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)):
        body = m.group(1)
        if not body.strip() or any(body.strip().startswith(h) for h in heads) or (max_chars and len(body) > max_chars):
            skipped += 1
            continue
        line = html[:m.start(1)].count("\n") + 1
        (out / f"script{i:02d}_line{line}.js").write_text(body, encoding="utf-8")
        kept += 1
    return kept, skipped


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("out_dir")
    ap.add_argument("--vendor-dir", action="append", default=[])
    ap.add_argument("--max-chars", type=int, default=0)
    a = ap.parse_args()
    k, s = extract(a.html, a.out_dir, a.vendor_dir, a.max_chars)
    print(f"extracted {k} own scripts, skipped {s} -> {a.out_dir}")
    sys.exit(0 if k else 1)
