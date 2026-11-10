"""Backtests. Replace `build_under_test` and the export function call with your own, keep the structure."""
import json, pathlib, pytest
from golden_lib import GOLDEN, SCENARIOS, KNOWN_DIFFERENCES, export_text, without_known_differences, first_mismatch

BUILD = "path/or/url/of/the/build/under/test"          # FILL IN


def read(sub, name):
    return (GOLDEN / sub / f"{name}.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", SCENARIOS)
def test_current_build_reproduces_its_golden_results_exactly(name):
    got, want = export_text(BUILD, SCENARIOS[name]), read("current", name)
    assert got == want, first_mismatch(want.split("\n"), got.split("\n"))


@pytest.mark.parametrize("name", SCENARIOS)
def test_current_golden_agrees_with_the_oracle_apart_from_known_differences(name):
    old, new = without_known_differences(read("oracle", name)), without_known_differences(read("current", name))
    assert old == new, first_mismatch(old, new)


def test_oracle_files_come_from_the_frozen_release():
    """SOURCE.json records which release produced the oracle files; its fingerprint must match the release manifest."""
    src = json.loads((GOLDEN / "oracle" / "SOURCE.json").read_text())
    manifest = json.loads(pathlib.Path("releases/MANIFEST.json").read_text())["files"]
    assert manifest[src["release"]]["sha256"] == src["sha256"]


def test_every_scenario_has_both_golden_files():
    for name in SCENARIOS:
        assert (GOLDEN / "current" / f"{name}.txt").is_file() and (GOLDEN / "oracle" / f"{name}.txt").is_file()


def test_the_known_differences_list_stays_small_and_explained():
    assert KNOWN_DIFFERENCES == set()          # FILL IN the exact set; a change here forces a conscious edit and a commit message


def test_the_backtest_would_notice_a_tiny_change_in_a_result():
    """Sensitivity: perturb a number by 0.001 and prove the comparison fails. Otherwise a loose comparison would pass silently."""
    name = next(iter(SCENARIOS))
    lines = read("current", name).split("\n")
    i = next(n for n, ln in enumerate(lines) if any(ch.isdigit() for ch in ln))
    lines[i] = lines[i].replace(next(tok for tok in lines[i].replace(",", " ").split() if tok.replace(".", "", 1).isdigit()), "999.001", 1)
    assert first_mismatch(read("current", name).split("\n"), lines) is not None
