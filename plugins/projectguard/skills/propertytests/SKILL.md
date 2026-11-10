---
name: propertytests
description: Write property tests, which state rules that must hold for every result whatever the numbers are, and cross view tests that compare a number shown in two places. Catches wrong answers that regenerated golden files would hide. Covers the families of rules (conservation, scaling, ordering, containment, nothing silently lost, consistency between views, invariance), tolerant number comparison, and how to prove the tests can fail. Use when the user wants stronger tests than exact comparisons, wants to find bugs in calculations, or says a number appears in several places.
---

# propertytests: rules that must always be true

A golden file test says "the answer is exactly this". A property test says "whatever the answer is, it must obey these rules". If someone breaks a formula and then regenerates the golden files to make the red tests green, the exact comparison agrees with the bug, but the rules do not.

## Families of rules (find the ones that fit the project)

1. **Conservation / formula of parts.** A derived value equals its formula from the parts, for every row: concentration equals amount divided by volume; total equals the sum of items; percentages add to 100.
2. **Scaling.** Change one input by a known factor and the output scales by the known factor: double the volume, halve the concentration, leave the amount untouched.
3. **Ordering.** A ranked list is sorted; ranks are within 1..N; best rank is not worse than worst rank.
4. **Containment.** An interval contains its estimate (low <= estimate <= high); a value stays inside its valid range.
5. **Nothing silently lost.** Every input item is either in the output or has a stated reason ("not detected", "not ranked"). The set of names out equals the set of names in.
6. **Invariance.** A setting that must not change results does not (display language, row order, file name).
7. **Consistency between views.** A number or a conclusion shown in two places must agree: the ranking table, a pairwise matrix and a summary sentence ("X of Y pairs differ"); the on screen report and the exported file; a headline count and the rows beneath it.
8. **Idempotence and round trip.** Export then import gives the same state; applying an operation twice equals applying it once.
9. **Monotonicity.** More of the input never gives less of the output where the domain says so.

## Steps

1. Read the output format and the code that computes it. Write the rules down in plain words first, as a numbered list, with the reason each must hold.
2. Parse the saved result files (golden files) into tables. Keep the parser tiny and shared (one function), and allow a missing table (legitimate when nothing could be produced).
3. Write one test per rule, parametrized over EVERY scenario and over both the current results and the oracle results. Numbers in files are rounded: compare with a tolerance (a relative difference of 0.002 is typical), never with `==`.
4. Add cross view tests inside the UI/report tests (see `uitests`): parse the report and compare it with the file.
5. Prove each test can fail: break the code in a scratch copy, regenerate the golden files from the broken build (the shortcut someone might take), and confirm the property tests still fail. If they pass, the rule is too weak or does not cover the breakage. See `mutationcheck`.

## Traps

* **Tie and unranked rows.** Real outputs contain rows without a number (not detected, not ranked). The parser and rules must handle them (ranked rows are those with a number; unranked rows must state a reason). A first version of our ranking rule crashed on these rows.
* **Counting rows that are not items.** A table can have an extra "not ranked" row; the headline count counts only numbered rows.
* **Half way rounding.** Two displays rounded at different precision can disagree at the edge (39.05 shows as 39.1 in one and 39.0 in the other). Compare within the rounding step.
* **A rule that cannot fail.** Parametrized tests over an empty list pass silently. Assert the list is not empty.
* **Randomized inputs.** For inputs you can generate, a property based library such as Hypothesis can try many cases; add it only if the project can produce valid random inputs cheaply. Saved scenarios are enough to start.

## Template

`assets/test_properties.py` contains a parser and one example for each family. Replace the example rules with the real ones.

## Honest limits

Properties only catch breakages that violate a rule you thought of. Pair them with exact golden files and an oracle; each layer catches different mistakes.
