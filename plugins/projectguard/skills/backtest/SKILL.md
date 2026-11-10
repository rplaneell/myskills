---
name: backtest
description: Backtest a project so its results never change by accident. Golden files (saved trusted results compared exactly on every push), an independent oracle from an older trusted version with an explicit allowlist of explained differences, scenarios that vary the settings a person can change, sensitivity checks that prove a tiny change is noticed, and rules for when a golden file may be regenerated. Works for web tools, command line tools and libraries. Use when the user wants to do backtesting, regression testing, make results traceable, lock statistics or calculations, or never let outputs change unless asked.
---

# backtest: replay known inputs, demand the same answers

Backtesting means feeding known inputs through the project and checking that the answers are exactly the saved ones. If a result is ever wrong or different, a test fails on the exact line. It is the main defence for projects whose value is in their numbers.

## Core pieces

1. **Scenarios.** A registry of named inputs. Cover the defaults AND every setting a person can change (amounts, units, language, selections, options). A backtest of defaults only protects the defaults. Include messy and edge case inputs, including one where nothing is detected.
2. **Golden files (`golden/current/`).** The exact result text of each scenario, accepted by the owner. The test recomputes and demands equality. Remove only what legitimately differs between runs (timestamps, ids), by named patterns, so everything else is compared exactly.
3. **An oracle (`golden/oracle/`).** If an older trusted version exists (a frozen release), run the same scenarios through it and save its outputs. The current version must agree with the oracle on everything except an explicit, explained allowlist of lines. The oracle cannot be talked away by regenerating the current golden files.
4. **Sensitivity checks.** A test that perturbs one number by a tiny amount (0.001) and proves the comparison fails. Another test that proves each changed setting really changes the output (a scenario that silently does nothing is worthless), and that a setting which must not change results (language) gives identical results.
5. **A provenance test:** the oracle files record which release produced them (name and SHA 256 fingerprint), and a test checks that against the release manifest (see `releaseintegrity`).

## Steps (ask before touching the repository)

1. List what the project produces that must not change. Choose the exported text, file or output that carries all important numbers.
2. Copy the templates from `assets/` (`golden_lib.py`, `test_golden.py`, `make_golden.py`), fill in the marked places: scenarios, volatile patterns, known differences, how to run one scenario (`export_text_cli` or `export_text_browser`).
3. Explore first: run each scenario on both the current build and the oracle, and diff them. Do this BEFORE writing the allowlist, so each allowed difference is understood and named, with a reason in a comment.
4. Generate: `make_golden.py current`, then `make_golden.py oracle` (it refuses if the release no longer matches its fingerprint). Check the first generation reproduces byte for byte when run twice (stable).
5. Add the tests and run them. Then PROVE they can fail: in a scratch copy make a formula slightly wrong and watch the golden tests fail on the exact line (use `mutationcheck`).
6. Add the comparison to CI. Commit the golden files and the tests together, with a message that says no result changed.

## Compare lists, not positions

When one side has an extra line, comparing by position shifts every later line and creates false alarms. Remove the allowed lines from BOTH sides first, then compare the remaining lists. Report the first mismatching line with a short excerpt.

## When may a golden file change?

Only when the owner asked for a result to change. Then: rebuild, run `make_golden.py current`, READ the diff, keep it in the same commit as the change, and say in the commit message which numbers moved and why. Never regenerate to make a red test green without understanding it. If the oracle or the property tests still fail after you regenerate, the change is probably a bug. See `references/golden_rules.md`.

## What to report

* How many scenarios, what they cover, what is NOT covered (be specific: other outputs such as charts, PDFs, other languages).
* That the comparison against the oracle agrees (or the exact list of differences).
* The proof that a tiny change fails.

## Honest limits

* Only the compared output is protected. If a chart is wrong but the exported numbers are right, the backtest passes.
* Golden files can encode a bug that existed on the day they were accepted. The oracle and the property tests (see `propertytests`) are the defence.
* Floating point text can differ across machines or libraries; if so, round to a stated number of digits in the exported text rather than loosening the comparison.
