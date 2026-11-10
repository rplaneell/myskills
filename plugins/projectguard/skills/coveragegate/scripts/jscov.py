"""JavaScript coverage of the page, measured while the browser tests run (pytest plugin, off by default).

Coverage means: which lines and functions of OUR JavaScript ran at least once during the tests. Code that never ran
is not checked by any test. Vendored libraries (code copied in unchanged) are left out because they are not your code: set JSCOV_VENDOR_DIR to their folder.

Place this file and jscov_math.py in your tests folder and add  pytest_plugins = ["jscov"]  to conftest.py when JSCOV=1.
Switch on:        JSCOV=1 python3 -m pytest tests -q
Enforce the floor JSCOV=1 JSCOV_ENFORCE=1 python3 -m pytest tests -q     (CI does this)
The floor is in tests/coverage_floor.json. Raise it in a commit when coverage improves; never lower it to hide a loss.
Only enforce on a FULL run: a partial run (for example -k) always looks worse.
The browser's own recorder (Chrome DevTools Protocol, "precise coverage") is used, so this works in Chromium only.
"""
import hashlib, json, os, pathlib

from playwright.sync_api import BrowserContext

from jscov_math import check_floor, summarize, vendor_heads

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL_SUFFIX = os.environ.get("JSCOV_URL_SUFFIX", ".html")          # only scripts of pages whose URL ends like this are counted
FLOOR_FILE = ROOT / os.environ.get("JSCOV_FLOOR", "tests/coverage_floor.json")
REPORT_FILE = ROOT / "build" / "js_coverage.json"

DATA = {}        # sha1 of script source -> {"source", "covered" (bytearray of 0/1), "funcs": {(name, start, end): ever_called}}
_sessions = {}   # id(context) -> [(page, cdp session)]
_orig_new_page, _orig_close = BrowserContext.new_page, BrowserContext.close


def _new_page(self, *args, **kwargs):
    page = _orig_new_page(self, *args, **kwargs)
    cdp = self.new_cdp_session(page)
    cdp.send("Debugger.enable")
    cdp.send("Profiler.enable")
    cdp.send("Profiler.startPreciseCoverage", {"callCount": True, "detailed": True})
    _sessions.setdefault(id(self), []).append((page, cdp))
    return page


def _collect(cdp):
    try:
        scripts = cdp.send("Profiler.takePreciseCoverage")["result"]
    except Exception:
        return
    for sc in scripts:
        if not sc["url"].endswith(URL_SUFFIX):
            continue
        try:
            src = cdp.send("Debugger.getScriptSource", {"scriptId": sc["scriptId"]})["scriptSource"]
        except Exception:
            continue
        d = DATA.setdefault(hashlib.sha1(src.encode()).hexdigest(),
                            {"source": src, "covered": bytearray(len(src)), "funcs": {}})
        mask = bytearray(b"\x01" * len(src))
        for fn in sc["functions"]:
            for r in fn["ranges"]:                       # outer ranges come first, inner ones override them
                mask[r["startOffset"]:r["endOffset"]] = bytes([1 if r["count"] > 0 else 0]) * (r["endOffset"] - r["startOffset"])
            r0 = fn["ranges"][0]
            key = (fn["functionName"], r0["startOffset"], r0["endOffset"])
            d["funcs"][key] = d["funcs"].get(key, False) or r0["count"] > 0
        for i, v in enumerate(mask):
            if v:
                d["covered"][i] = 1


def _close(self, *args, **kwargs):
    for _page, cdp in _sessions.pop(id(self), []):
        _collect(cdp)
    return _orig_close(self, *args, **kwargs)


BrowserContext.new_page, BrowserContext.close = _new_page, _close


def pytest_sessionfinish(session, exitstatus):
    scripts = [{"source": d["source"], "covered": "".join(map(str, d["covered"])),
                "funcs": [[n, s, e, c] for (n, s, e), c in d["funcs"].items()]} for d in DATA.values()]
    result = summarize(scripts, vendor_heads())
    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(json.dumps(result, indent=1), encoding="utf-8")
    floor = json.loads(FLOOR_FILE.read_text())
    problems = check_floor(result, floor)
    session.config._pq_cov = (result, floor, problems)
    if problems and os.environ.get("JSCOV_ENFORCE") == "1" and session.exitstatus == 0:
        session.exitstatus = 1


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not hasattr(config, "_pq_cov"):
        return
    result, floor, problems = config._pq_cov
    tr = terminalreporter
    tr.section("JavaScript coverage of the page")
    tr.write_line(f"lines run by tests:     {result['lines_covered']}/{result['lines_total']} = {result['lines_percent']}%   (floor {floor['lines_percent']}%)")
    tr.write_line(f"functions called:       {result['functions_covered']}/{result['functions_total']} = {result['functions_percent']}%   (floor {floor['functions_percent']}%)")
    for p in problems:
        tr.write_line("COVERAGE BELOW THE FLOOR: " + p, red=True)
    if not problems and (result["lines_percent"] - floor["lines_percent"] > 2):
        tr.write_line("coverage is well above the floor: consider raising tests/coverage_floor.json in a commit")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### JavaScript coverage\n\nLines run: **{result['lines_percent']}%** (floor {floor['lines_percent']}%), "
                    f"functions called: **{result['functions_percent']}%** (floor {floor['functions_percent']}%)\n")
