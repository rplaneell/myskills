---
name: codescan
description: Free static code scanning with Semgrep for any project, with your own rules and two built in guards that stop the scanner from going blind (a planted bad fixture every rule must fire on, and a check that the number of files scanned equals the number present). Includes extracting inline scripts from a built single file HTML page, browser risk rules (HTML built from variables, dynamic code, network use, storage, navigation, window messages), a CI workflow, and how to triage findings honestly. Use when the user asks for code scanning, SAST (static application security testing), CodeQL alternatives, XSS (cross site scripting) review, or to check a codebase for risky patterns.
---

# codescan: look for risky code patterns, and prove the scanner can see

Semgrep is a code scanner with a free command line version. It reads code (without running it) and matches it against rules. It replaces CodeQL where that is paid (private repositories on a free plan). The danger with any scanner is silence: "zero findings" can mean "clean" or "I looked at nothing". This skill is built around telling the two apart.

## The two guards (do not skip them)

1. **Self test.** A folder of deliberately bad code (`assets/bad_example.js`) is scanned first. EVERY rule must fire on it, otherwise the run fails with "SELF TEST FAILED: the scanner is blind to ...". This is what caught us when the public rule sets found nothing in code with obvious bugs.
2. **Blind scan guard.** After the real scan, the number of files Semgrep reports as scanned must equal the number of files present. Otherwise: "BLIND SCAN". Semgrep silently skips folders named `build` and `tests` and files ignored by Git. We first scanned a folder called `build/` and got "0 findings" with exit code 0.

`scripts/semgrep_check.py` does both, then prints a table of findings per rule and severity. It is report only by default; `--block-errors` makes ERROR level findings fail the run.

## Steps (ask before changing the repository)

1. Install Semgrep in a private environment: `pip install semgrep` (pin the version you tested). Switch metrics off (the script does): nothing about the project is uploaded.
2. Decide what to scan. For a normal codebase, scan the source folders. For a single file web page, extract the inline scripts first with `scripts/extract_inline_scripts.py page.html semgrep_input --vendor-dir src/vendor` (skips vendored libraries because they are not your code). Fragments that start with `<script>` do not parse as JavaScript, which is why you scan the built page's real scripts.
3. Put the rules in `.semgrep/rules.yml` (start from `assets/rules_browser.yml`: HTML built from variables, dynamic code, network APIs, storage and cookies, navigation, window messages) and the planted bad file in `.semgrep/fixtures/`. Adapt the rules to your project type; write a rule for each risk you care about.
4. Run: `python3 semgrep_check.py --rules .semgrep/rules.yml --fixtures .semgrep/fixtures --target semgrep_input --prepare "python3 tools/extract_inline_scripts.py dist/app.html semgrep_input"`.
5. Add the CI workflow (`assets/semgrep_workflow.yml`), report only first. Pin its actions.
6. **Show the owner the first report before making anything blocking**, in plain words: what each rule checks, how many findings, and for each group whether it is real, a false alarm, or unknown.
7. Later: make the zero finding rules blocking (dynamic code, network use), and add a ceiling on the count of the noisy rule so it cannot grow without review.

## Triage honestly

A finding is not a vulnerability until you show how hostile input reaches it. "HTML built from a variable" is a place to test, not a bug. Settle it with the `hostileinput` skill: put hostile text into every entry point and look at the page structure. Say what that does not prove (it covers entry points a person can reach, not every code path). Never write "safe" about the whole set.

## Honest limits

* Your own rules only find what you wrote rules for; they are narrower than a commercial engine.
* Some public registry rules need a free login; do not log in on the owner's behalf. Prefer your own rules, which also work offline.
* A clean scan means "none of these patterns", not "secure".

## Files

* `scripts/semgrep_check.py`, `scripts/extract_inline_scripts.py`
* `assets/rules_browser.yml`, `assets/bad_example.js`, `assets/semgrep_workflow.yml`
* `references/rules_and_limits.md`
