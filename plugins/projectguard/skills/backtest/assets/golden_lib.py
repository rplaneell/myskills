"""Golden file backtests: shared pieces. Copy next to your tests and fill in the three marked places.

A golden file is a saved, trusted result. A backtest replays known inputs through the tool and demands the SAME result.
Two sets are kept: current/ (what this version produced when the owner accepted it) and oracle/ (what an older trusted
version produced, used as an independent answer key). See the SKILL.md next to this file for the rules.
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
GOLDEN = pathlib.Path(__file__).resolve().parent / "golden"

# 1) FILL IN: every input scenario. name -> anything your export function needs (files, settings, command line).
SCENARIOS = {
    # "base": {"inputs": ["examples/a.csv", "examples/b.csv"]},
    # "volume_20": {"inputs": [...], "setting": {"volume": "20"}},
}

# 2) FILL IN: lines (by their FIRST field) that are ALLOWED to differ between the oracle and the current version.
#    Each entry is a known, explained difference. Anything else that differs is a failure.
KNOWN_DIFFERENCES = set()          # e.g. {"auto_position", "derived_size", "setting_only_in_old_version"}

# 3) FILL IN: the only things that legitimately change between runs, as regular expressions (timestamps, run ids, temp paths).
VOLATILE = [re.compile(r"\d{4}-\d\d-\d\dT[\d:.]+Z")]


def normalize(text):
    """Remove what changes between runs and unify line endings, so the comparison is exact on everything else."""
    text = text.replace("\r\n", "\n")
    for rx in VOLATILE:
        text = rx.sub("<VOLATILE>", text)
    return text


def without_known_differences(text):
    return [ln for ln in text.split("\n") if ln.split(",")[0] not in KNOWN_DIFFERENCES]


def first_mismatch(a_lines, b_lines):
    """Describe the first difference between two lists of lines, or None when identical."""
    if len(a_lines) != len(b_lines):
        return f"line count {len(a_lines)} versus {len(b_lines)}"
    for n, (x, y) in enumerate(zip(a_lines, b_lines), 1):
        if x != y:
            return f"line {n}: {x[:90]!r} versus {y[:90]!r}"
    return None


# 4) FILL IN: how to run ONE scenario against ONE build and get its result text. Two common shapes follow.
def export_text(build, scenario):
    """build = path or URL of the thing under test, scenario = a value of SCENARIOS. Return the result as text."""
    raise NotImplementedError("see export_text_cli and export_text_browser below and delete the one you do not need")


def export_text_cli(build, scenario):
    """A command line tool or script: run it and take its output."""
    import subprocess
    r = subprocess.run([build, *scenario["inputs"]], capture_output=True, text=True, check=True)
    return normalize(r.stdout)


def export_text_browser(browser, page_uri, scenario, setup=None):
    """A web page: load inputs, optionally change settings with setup(page), trigger the export download, read it."""
    ctx = browser.new_context(accept_downloads=True)
    try:
        pg = ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(page_uri)
        # pg.set_input_files("#fileA", scenario["inputs"][0]) ...
        if setup:
            setup(pg)
        with pg.expect_download(timeout=10000) as dl:
            pg.evaluate("exportResults()")          # whatever triggers your download
        assert not errors, errors
        return normalize(pathlib.Path(dl.value.path()).read_text(encoding="utf-8"))
    finally:
        ctx.close()
