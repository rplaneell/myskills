"""The pure arithmetic behind the JavaScript coverage numbers (no browser, no patching, safe to import in tests).

See tests/jscov.py for what coverage means here and how to switch it on.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def vendor_heads():
    """First 300 characters of each vendored library (folder in JSCOV_VENDOR_DIR, default src/vendor; empty means none)."""
    import os
    folder = os.environ.get("JSCOV_VENDOR_DIR", "src/vendor")
    if not folder or not (ROOT / folder).is_dir():
        return []
    return [p.read_text(encoding="utf-8").strip()[:300] for p in sorted((ROOT / folder).glob("*.js"))]


def summarize(scripts, vendor):
    """scripts: list of {"source", "covered", "funcs": [[name, start, end, called]]}. Returns totals and a per script list."""
    lines_total = lines_cov = funcs_total = funcs_cov = 0
    per_script, never_called = [], []
    for d in scripts:
        src = d["source"]
        if any(src.strip().startswith(v) for v in vendor):
            continue
        cov, off, lt, lc = d["covered"], 0, 0, 0
        for ln in src.split("\n"):
            s = ln.strip()
            first = off + (len(ln) - len(ln.lstrip()))
            if s and not s.startswith(("//", "/*", "*")) and s not in ("}", "};", "});", "{", ");"):
                lt += 1
                lc += 1 if (first >= len(cov) or str(cov[first]) in ("1", "49")) else 0   # 49 is the character "1"
            off += len(ln) + 1
        ft = len(d["funcs"])
        fc = sum(1 for f in d["funcs"] if f[3])
        never_called += [f[0] for f in d["funcs"] if not f[3] and f[0]]
        lines_total, lines_cov, funcs_total, funcs_cov = lines_total + lt, lines_cov + lc, funcs_total + ft, funcs_cov + fc
        head = " ".join(src.strip()[:90].replace("/*", "").replace("*/", "").replace("=", "").split())[:50]
        per_script.append({"name": head, "lines": lt, "lines_covered": lc})
    pct = lambda a, b: round(100.0 * a / b, 2) if b else 0.0
    return {"lines_total": lines_total, "lines_covered": lines_cov, "lines_percent": pct(lines_cov, lines_total),
            "functions_total": funcs_total, "functions_covered": funcs_cov, "functions_percent": pct(funcs_cov, funcs_total),
            "never_called_named": sorted(set(never_called)), "scripts": per_script}


def check_floor(result, floor):
    """Return a list of problems (empty when coverage is at or above the floor)."""
    out = []
    for key in ("lines_percent", "functions_percent"):
        if result[key] < floor[key]:
            out.append(f"{key.replace('_', ' ')} is {result[key]}, below the floor of {floor[key]}")
    return out
