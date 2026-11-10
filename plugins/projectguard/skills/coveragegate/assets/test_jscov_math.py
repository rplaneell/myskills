"""The coverage arithmetic must be right, or the floor in CI means nothing. No browser needed."""
import json, pathlib
from jscov_math import summarize, check_floor

CODE = "var a = 1;\nvar b = 2;\n// a comment\nif (a) {\n  b = 3;\n}\n"      # 4 code lines; the comment and the lone } are ignored


def script(covered_char_at, funcs=None, source=CODE):
    """covered: '1' everywhere except the first character of the lines named in covered_char_at (set to '0')."""
    cov = ["1"] * len(source)
    off = 0
    for i, ln in enumerate(source.split("\n"), 1):
        if i in covered_char_at:
            cov[off + (len(ln) - len(ln.lstrip()))] = "0"
        off += len(ln) + 1
    return {"source": source, "covered": "".join(cov), "funcs": funcs or []}


def test_everything_covered_is_100_percent_and_comments_and_braces_are_ignored():
    r = summarize([script(set())], [])
    assert (r["lines_total"], r["lines_covered"], r["lines_percent"]) == (4, 4, 100.0)


def test_uncovered_lines_lower_the_percentage():
    r = summarize([script({2, 5})], [])
    assert (r["lines_total"], r["lines_covered"], r["lines_percent"]) == (4, 2, 50.0)


def test_vendored_scripts_are_left_out():
    vendor_src = "/*! somelib vendored library */ var x = 1;\nvar y = 2;\n"
    r = summarize([script(set()), script({1, 2}, source=vendor_src)], [vendor_src.strip()[:300]])
    assert r["lines_total"] == 4 and r["lines_percent"] == 100.0


def test_functions_are_counted_and_never_called_names_are_listed():
    funcs = [["loadGel", 0, 10, True], ["autoRf", 11, 20, False], ["", 21, 30, False], ["makePdf", 31, 40, False]]
    r = summarize([script(set(), funcs)], [])
    assert (r["functions_total"], r["functions_covered"]) == (4, 1)
    assert r["never_called_named"] == ["autoRf", "makePdf"]            # anonymous functions have no name to list


def test_floor_check_passes_at_the_floor_and_fails_below_it():
    floor = {"lines_percent": 76.0, "functions_percent": 78.0}
    assert check_floor({"lines_percent": 76.0, "functions_percent": 78.0}, floor) == []
    assert check_floor({"lines_percent": 90, "functions_percent": 90}, floor) == []
    bad = check_floor({"lines_percent": 75.99, "functions_percent": 70.0}, floor)
    assert len(bad) == 2 and "lines percent" in bad[0]


def test_the_floor_file_is_sane():
    f = json.loads((pathlib.Path(__file__).parent / "coverage_floor.json").read_text())
    assert set(f) == {"lines_percent", "functions_percent"}
    assert all(50 <= v <= 100 for v in f.values()), f           # a floor below 50 would protect nothing
