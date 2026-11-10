---
name: coveragegate
description: Measure which lines and functions of JavaScript run during browser tests, using Chromium's precise coverage through a pytest plugin, and enforce a minimum (a floor) in CI so coverage can only go up. Covers excluding vendored libraries, measuring twice to know the wobble, choosing and ratcheting the floor, enforcing only on full runs, and the honest meaning of coverage. Use when the user asks for test coverage, wants to know what is untested, or wants CI to fail when tests are removed or untested code is added.
---

# coveragegate: know what the tests run, and stop it from falling

Coverage means: of all lines of your code, how many ran at least once while the tests ran. A line that never runs is not checked by any test: if it broke, nobody would notice. A coverage floor is a saved minimum that CI enforces, so nobody can quietly delete tests or add untested code.

## What coverage does NOT mean

Running a line is not the same as checking its result. A test can run code and assert nothing useful. So coverage gives an UPPER LIMIT of how well protected you are. Pair it with `mutationcheck`, which shows whether the tests would notice a wrong result. Do not chase 100 percent: defensive branches that cannot happen produce tests that check little. About 90 to 93 percent is a sensible target for a UI heavy project (our own estimate, not a promise).

## How it works (browser projects)

Chromium can record exactly which parts of each script ran ("precise coverage", through the Chrome DevTools Protocol). The plugin `scripts/jscov.py` attaches to every page the tests open, collects the recorder's data when the page closes, merges it across all tests, and prints a summary. `scripts/jscov_math.py` holds the pure arithmetic (no browser), so it can be unit tested (`assets/test_jscov_math.py`).

Chromium only. It measures scripts of the page whose URL ends with `JSCOV_URL_SUFFIX` (default `.html`), excluding vendored libraries found in `JSCOV_VENDOR_DIR` (default `src/vendor`; set it empty for none).

## Steps (ask before changing the repository)

1. Copy `jscov.py` and `jscov_math.py` into the tests folder; in `conftest.py` add `if os.environ.get("JSCOV") == "1": pytest_plugins = ["jscov"]`. Put `assets/coverage_floor.json` at `tests/coverage_floor.json` with floors of 0 for now.
2. Run the full suite once: `JSCOV=1 python3 -m pytest tests -q`. Report lines and functions, and the per script breakdown (which modules are weakest) in plain words.
3. **Measure twice.** Identical runs differ by a line or a function. Choose the floor about one and a half points below the measured value, so a slightly different browser on the CI machine does not fail the build by accident. Remember the first CI run is the real calibration; if CI fails only on coverage with numbers just under the floor, recalibrate instead of assuming a real loss.
4. Unit test the arithmetic (`test_jscov_math.py`): all covered is 100 percent, uncovered lines lower it, comments and lone braces are ignored, vendored scripts are left out, functions are counted, the floor check passes at the floor and fails below.
5. **Prove the enforcement works:** run a small subset of tests with `JSCOV_ENFORCE=1`; coverage will be far below the floor, the run must exit with code 1 and name both numbers. With enforcement off the same run must exit 0 and only report. With coverage switched off, tests behave as before.
6. Wire it into CI: the test step gets `env: JSCOV: "1"` and `JSCOV_ENFORCE: "1"`. The plugin can append a summary to `GITHUB_STEP_SUMMARY`.
7. **Ratchet.** After each batch of new tests, measure again and raise the floor in its own commit with the numbers in the message. Never lower the floor to hide a loss; investigate it.

## Enforce only on a full run

A partial run (`-k`, one file) always looks worse. Enforcement is an environment variable that only CI sets.

## Choosing what to test next

The report shows lines never run per script. Typical biggest holes: output features (PDF, print, reports), photo or file loading, error branches, rarely used controls. Test the ones that produce what people read or save first. See `uitests`.

## Honest limits

* It measures lines that ran, not lines whose result was checked.
* The wobble between machines means a floor is a safety net, not a precise instrument.
* Source maps: if the tests run a built file, line numbers refer to the built file. Use the per script names and the dist line numbers to find the source.
