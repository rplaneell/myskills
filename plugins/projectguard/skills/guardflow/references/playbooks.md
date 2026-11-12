# Playbooks

Each playbook is a list of steps. A step names the skill, the proof it must produce, and whether it needs the owner's yes.
Ledger means: write a row with `ledger.py add` (outcome, proof, detail, limit).

## A. Audit (read only first)

1. Intake questions (public or private, server or not, what must not change, old trusted version, what is shipped).
2. Recon, no permission needed:
   * `releaseintegrity`: build twice and compare; compare the shipped file with a fresh build. Ledger.
   * `secretguard`: scan the whole history; list tracked secret shaped files. Ledger.
   * `depaudit`: `run_audits.sh` in a scratch copy; check for vendored libraries with no list. Ledger.
   * `codescan`: self test on a planted bad file first; then scan; confirm the scanned count. Ledger.
   * `repocontrols`: which protections exist (rules, hooks, CI), which are paid and missing.
   * Tests: count them, measure coverage (`coveragegate`) if possible, list what the backtests cover (`backtest`).
   * `securityaudit`: fill in the checklist with the architecture.
3. Report in plain words with the ledger. No changes made. Offer playbook B or C for the gaps, with a recommended first step.

## B. Set up from scratch (ask before each commit)

1. `secretguard`: ignore rules, history scan, local blocker (prove with the fake key test), CI scan with a fingerprint checked download.
2. `cihardening`: pin actions, least privilege, Dependabot, rebuild check.
3. `repocontrols`: contributing rules, rules job (prove each rule can fail), push blocker (prove against a fake remote).
4. `depaudit`: audits, vendored list and test, weekly schedule.
5. `ownersteps`: the checker and the commands for the owner. Record as reported until the checker output is seen.
6. `codescan`: rules, planted fixture, guards, report only at first.
7. Plan document with the paid versus free table. Ledger after each step.

## C. Strengthen tests

1. `backtest`: scenarios for defaults AND every changed setting; oracle if an old trusted version exists; sensitivity test.
2. `propertytests`: rules for every result; cross view comparisons.
3. `hostileinput`: entry points times three attack styles; detector self check; break test of the escaping.
4. `uitests`: clicking tests for the weakest areas first (use `coveragegate` to find them).
5. `coveragegate`: measure twice, set the floor with room, enforce only on full runs, raise after each batch.
6. `mutationcheck`: break the core calculations; each survivor becomes a test.
7. Commit per batch; read CI; ledger.

## D. Release gate

1. Working tree clean; branch up to date.
2. Run everything: tests (golden, oracle, property, hostile, clicking), coverage floor, `codescan`, `depaudit`, `repocontrols` rules.
3. `releaseintegrity`: rebuild from the tag candidate; fingerprint; add to the manifest naming the commit.
4. `mutationcheck` on the areas changed since the last release.
5. Ledger review: no open item without an owner decision. Report. Then, only with a yes: tag and publish.

## E. Periodic review

1. Read the scheduled audit results; run `depaudit` locally if unreadable.
2. Read the newest CI runs for every workflow.
3. Check the ledger for open and partial items older than the last review.
4. Ask the owner to run the checker again if hooks may have been lost (new computer).
5. Report only what changed.

## F. Leak response (speed over tidiness)

1. Revoke at the provider and create a new secret (`secretguard` leak response). Check the provider logs for use.
2. Remove from the code; optional history cleanup only with a safety copy and a yes.
3. Find the missing layer (hook not installed, file not ignored, screenshot) and add it. Ledger the incident with its lesson.

## G. Evaluate and port a shipped file

1. `releaseintegrity` Phase 0: compare, determinism, freeze and fingerprint.
2. `porting`: `script_inventory.py`, plan document, decisions for the owner.
3. `backtest`: the shipped file as the oracle.
4. Port step by step with the owner's yes for each step.

## H. Visual report

1. Make sure the ledger is current and valid.
2. `ledger.py export-checks`, then build the other tables from recorded facts (nothing invented; null when not recorded).
3. `securityreport`: page, local harness and render checks, look at screenshots, PDF, publish.
4. Hand over: which numbers are your own record, what is a snapshot, what the owner can ask for next.
