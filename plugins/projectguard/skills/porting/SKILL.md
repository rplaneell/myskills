---
name: porting
description: Bring an old shipped build (a single file web page or any release whose source is unknown) into the repository's sources safely. Covers inventorying exactly what differs with a script comparison tool, classifying scripts as identical, changed, vendored, embedded media or only in the shipped file, ordering the work from most measurable to largest, using the old build as an oracle for every step, exit rules per step, decisions the owner must make (for example embedded video), and risks. Use when a shipped file is not rebuilt from the sources, when features exist only in a release, or when the user asks to port, migrate or reconcile an old version.
---

# porting: make the sources produce what people actually run

Sometimes the file users run was built somewhere else, by hand or from sources that are lost. Testing the sources then protects nothing that matters. The fix is not a rewrite: it is a measured, step by step port where the old file stays the trusted answer key until every difference is either ported or consciously dropped.

## Start with evidence, not assumptions

1. **Build the sources** in a scratch copy and compare with the shipped file: `scripts/script_inventory.py shipped.html fresh_build.html --vendor-dir src/vendor`. For each inline script of the shipped file it says:
   * `SAME`: identical to a script of the fresh build.
   * `CHANGED`: a similar script exists; it shows both sizes and the lines added and removed. This is where behaviour differs.
   * `VENDOR`: a copied in library.
   * `MEDIA`: embedded data such as a video, picture or font, with its decoded size and file type. These explain big size gaps and raise decisions (see below).
   * `ONLY`: nothing similar in the sources: a feature the sources do not have.
2. Read the headings and comments of each `ONLY` and `CHANGED` script. Write a one line description of the feature each represents. Check release notes or the changelog, but trust the code.
3. A first, crude comparison can mislead (we once paired modules with the wrong counterpart and printed wrong sizes). Use the tool's best match logic, and sanity check a few pairs by hand.
4. Check what the existing backtests already say. If the shipped file is an oracle (see `backtest`), the known differences between it and the build are already listed; each one belongs to a port step.

## Write the plan before any code (documentation only, ask before committing)

Put a `docs/PORTING_PLAN.md` in the repository with: why, the measured differences, the order, an exit rule per step, decisions for the owner, risks, and what done means. Use the template in `references/plan_template.md`.

## Order the steps

1. **Smallest and most measurable first:** the step whose effect shows in a backtest line. Example: a finder of a position in the data, whose output is a line in the results file that currently appears in the list of known differences. Exit rule: that entry leaves the list, and no headline number changes.
2. **Features that add a setting or output** next, each with a new scenario run through the OLD build FIRST to create its oracle file. Never write the expected result from the new code.
3. **Largest and riskiest** later (file writers, parsers of files people supply), preceded by hostile input and malformed file tests (`hostileinput`, `uitests`).
4. **Cosmetic and presentation layers** last, and only if the owner wants them in the product.
5. **Translations** grow with each step (new text needs its entries).

## For every step

1. Ask the owner before starting the step.
2. Create the oracle output from the old build for the new scenarios. Commit it with the manifest fingerprint of the old build.
3. Write or adapt the tests first (golden scenario, property rules, clicking tests as appropriate) and watch them fail on the current build.
4. Port the code in the smallest change that makes them pass. Keep the old file's behaviour, including its mistakes, unless the owner decides otherwise: a port is not a bug fix. Record any bug you notice separately.
5. Rebuild, run everything: golden and oracle comparison, property tests, hostile input, clicking tests, the code scan, the dependency audits, the coverage floor.
6. Raise the coverage floor if it rose. Update the list of known differences (remove the entry that is now gone). Commit with a message that says which numbers moved and why, then push and read the CI result.
7. Record the step in the ledger (`guardflow`).

## Decisions that belong to the owner (ask, do not decide)

* **Embedded media** (a video of about 1.6 MB stored as text in the page): is it part of the product, or only of a presentation edition? Its source file may exist only inside the shipped file (it can be decoded from the base64 text and committed as an asset). Large assets affect size, load time and the content policy.
* **Decorative layers** (animations, art edition): product or separate flavour?
* **Behaviour changes that alter a result line** to match the oracle: confirm first.
* **Variants.** A release file name that strings several words together (for example a style, a feature and an option) may list variants. Ask what each word means and which one the users run.
* **Priority** of the steps.

## What done means

All steps ported or consciously dropped, the oracle comparison has no known differences left, coverage floor, scans and audits green, a rebuild from a tagged commit gives a fingerprint recorded in the release manifest (`releaseintegrity`), and the manifest names the commit it was built from.

## Honest limits

* The inventory is evidence, not proof. Proof is a rebuild whose fingerprint matches, which may never be byte identical after a port; define done by the oracle comparison instead.
* A port can quietly change a number. That is why every step starts from an oracle file made by the old build.
* Features that write or parse files need the security treatment before they are ported, not after.
