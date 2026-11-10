---
name: mutationcheck
description: Mutation checking breaks code on purpose in small ways, one at a time, in a scratch copy, and verifies that at least one test fails for each break. Survivors reveal missing tests. Includes a runner script with a baseline guard and exactly one match guard, how to choose good mutants (calculations, thresholds, limits, names, cleanup, state), how to turn a survivor into a test, and honest limits. Use when the user wants to know whether the tests would really notice a bug, when raising confidence in calculations, or when coverage is high but trust is low.
---

# mutationcheck: would the tests notice a real bug?

A mutant is a small deliberate mistake: a factor changed, a threshold shifted, a cleanup removed. If the tests FAIL, the mutant is CAUGHT (good). If the tests still PASS, it SURVIVED: no test notices that kind of mistake, so a real bug like it would slip through. Survivors are the useful result.

Coverage says which lines ran. Mutation checking says whether running them was worth anything.

## Using the runner

`scripts/mutate.py spec.json --project . --exclude releases`

```json
{"test_command": "python3 -m pytest tests -q -x",
 "timeout": 900,
 "mutants": [
   {"name": "zoom in factor 0.7 instead of 0.6", "file": "dist/app.html",
    "old": "zoomAround(0.6)", "new": "zoomAround(0.7)"}
 ]}
```

What it guarantees:
* **Your files are never touched.** It works in a temporary copy.
* **Baseline guard:** the tests must pass on the unbroken code first. If they do not, it exits with code 2 and refuses to give results.
* **Exactly once guard:** the text to change must occur exactly once, otherwise the mutant is REJECTED (it would prove nothing or break the wrong thing).
* A timeout counts as caught (a hang is noticed).
* Exit code 1 if anything survived or was rejected (unless `--allow-survivors`).

Mutate the file the tests really run. If the tests use a built file, either mutate the built file (quick, fine for a check) or mutate the source and rebuild in the test command.

## Choosing good mutants

Pick mistakes a tired developer could make:
1. **Formulas and constants:** the calibration factor, a divisor, a unit conversion, a rounding precision, an off by one in a loop bound.
2. **Thresholds and limits:** a "greater than" shifted by 30 percent, a maximum raised from 40 to 60, a minimum changed.
3. **Defaults:** a default value, a default option.
4. **Disabled protections:** a read only flag turned off, a validation removed, an escape helper switched off.
5. **Names and labels** that tests compare: a file name, a title, a message.
6. **Cleanup and state:** a function that clears a temporary area no longer called; a reset that does nothing.
7. **Values used in two places:** change ONE of the places (this is what exposed a gap for us: the "which pairs differ" threshold changed in only one of two places survived until a test compared the summary sentence with the table).

Start with 5 to 10 mutants in the most important calculation, not hundreds. Each costs one test run.

## Turn survivors into tests

For each survivor ask: what visible behaviour would be different if this were wrong, and which existing test should have looked at it? Often the answer is "a number is shown in two places and nothing compares them" or "the test only checks that something happened, not what". Write the missing assertion, rerun the mutant, and confirm it is now CAUGHT. Keep the mutant list in the repository (a JSON file) so it can be rerun before releases.

## Honest limits

* A caught mutant only proves that kind of mistake is noticed. Survivors are findings; no survivors is not a proof of correctness.
* It is slow, so run it on demand or nightly, not on every push.
* Equivalent mutants (a change that does not alter behaviour) will survive; read the survivor before writing a test for it.
* Automatic mutation tools exist for many languages (for example Stryker for JavaScript, mutmut for Python); this runner is deliberately manual and tiny, so every mutant is one a human chose and understands.
