"""Property tests: rules that must hold for EVERY result, whatever the numbers are.

A golden file test says "the answer is exactly this". A property test says "whatever the answer is, it must obey these rules".
That catches wrong answers a regenerated golden file would otherwise hide (someone breaks a formula, regenerates the golden
files to make the red tests green, and the exact comparison now agrees with the bug).

Run them over the saved golden results (fast, no browser) AND, if you can, over freshly computed results.
Replace the example rules with the rules of YOUR domain. Good sources of rules are listed in the SKILL.md.
"""
import csv, io, pytest
from golden_lib import GOLDEN, SCENARIOS


def read_table(sub, name, header_start):
    """Parse the block of a results file that starts with a header line beginning `header_start` into a list of dicts."""
    lines = (GOLDEN / sub / f"{name}.txt").read_text(encoding="utf-8").split("\n")
    start = next((i for i, l in enumerate(lines) if l.startswith(header_start)), None)
    if start is None:
        return []                                   # a result file may legitimately have no such table (nothing to report)
    block = []
    for l in lines[start:]:
        if not l.strip():
            break
        block.append(l)
    return list(csv.DictReader(io.StringIO("\n".join(block))))


def close(a, b, rel=2e-3):
    """Numbers in files are rounded; compare with a tolerance, never with ==."""
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-12)


@pytest.mark.parametrize("sub", ["current", "oracle"])
@pytest.mark.parametrize("name", SCENARIOS)
def test_a_derived_value_equals_the_formula_of_its_parts(sub, name):
    # EXAMPLE of a "conservation" rule: total == amount / volume, whatever the inputs were.
    for row in read_table(sub, name, "id,"):
        if row.get("total"):
            assert close(float(row["total"]), float(row["amount"]) / float(row["volume"])), (name, row["id"])


@pytest.mark.parametrize("name", SCENARIOS)
def test_an_interval_contains_its_estimate(name):
    # EXAMPLE of a "containment" rule: low <= estimate <= high.
    for row in read_table("current", name, "id,"):
        if row.get("estimate"):
            assert float(row["low"]) <= float(row["estimate"]) <= float(row["high"]), (name, row["id"])


@pytest.mark.parametrize("name", SCENARIOS)
def test_a_ranking_is_ordered_and_nothing_disappears_without_a_reason(name):
    # EXAMPLES of "ordering" and "nothing silently lost" rules.
    rows = read_table("current", name, "rank,")
    ranked = [r for r in rows if r.get("value")]
    values = [float(r["value"]) for r in ranked]
    assert values == sorted(values, reverse=True), name
    for r in rows:
        if not r.get("value"):
            assert r["reason"].startswith("not ranked"), (name, r)      # every unranked item says why


def test_changing_a_setting_scales_the_result_by_the_expected_factor():
    # EXAMPLE of a "scaling" rule between two scenarios: doubling the volume halves the concentration, the amount is unchanged.
    base = {r["id"]: r for r in read_table("current", "base", "id,")}
    double = {r["id"]: r for r in read_table("current", "volume_x2", "id,")}
    for k in base:
        assert base[k]["amount"] == double[k]["amount"]
        assert close(float(double[k]["total"]), float(base[k]["total"]) / 2)


def test_two_views_of_the_same_number_agree():
    # EXAMPLE of a "cross view" rule: a number shown in a report must equal the same number in the exported file (to the digits shown).
    pass
