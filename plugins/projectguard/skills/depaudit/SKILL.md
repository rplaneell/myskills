---
name: depaudit
description: Audit a project's dependencies for known vulnerabilities with npm audit, pip audit and OSV Scanner, including libraries that were copied into the project (vendored) and are invisible to every normal audit. Covers running the audits safely in a scratch copy, a weekly scheduled CI workflow, a checksum verified scanner download, a list of vendored libraries for the scanner, a test that keeps that list and the library fingerprints honest, and how to read and report results. Use when the user asks for a dependency audit, vulnerability scan, supply chain check, SBOM (software bill of materials), or to know whether any library has a known flaw.
---

# depaudit: do any of our libraries have a known flaw?

A vulnerability audit compares the exact versions of the libraries a project uses with public databases of known flaws. It catches what nobody on the team knows about yet. It cannot catch flaws that are not published, and it only sees libraries that are written down somewhere it can read.

## The three audits, and what each sees

* **npm audit** reads `package-lock.json` (JavaScript packages used to build or run).
* **pip audit** reads `requirements.txt` (Python packages). Unpinned ranges such as `playwright>=1.45` are resolved to the newest allowed version, which is what a fresh install would get.
* **OSV Scanner** (Open Source Vulnerabilities, Google's scanner) reads lock files, requirements and SBOM files (software bill of materials: a list of ingredients) against the OSV database, which merges many sources. It is the only one of the three that can read a hand written list of libraries.

Run all three. Each has blind spots the others cover.

## The blind spot that matters most: copied in libraries

Many projects copy a library file straight into the page or the repository (a minified file under `src/vendor`). No lock file mentions it, so every audit above reports a clean result while knowing nothing about it. Close the gap:

1. Record each copied library in `THIRD_PARTY.md` with its version and the SHA 256 fingerprint of the file.
2. List the same libraries in `sbom/vendored.cdx.json` (CycloneDX format, with a `purl` such as `pkg:npm/name@1.2.3`) and give that file to the scanner as `-L sbom/vendored.cdx.json`.
3. Add `assets/test_vendored.py`: it fails if a file no longer matches its recorded fingerprint, if the file's own header states another version, or if the list names a different version. Without it an updated or swapped library would be audited at its OLD version.
4. Prove the test can fail in a scratch copy: change one byte, change a version in the list, change a version in the record. Each must fail.

Honest limit: libraries bundled inside a vendored file (its own dependencies) are not listed. Say so.

## Steps (ask before changing the repository)

1. **Read only first.** Run `scripts/run_audits.sh path/to/project`. It works on a scratch copy of the lock files, prints PASS, FAIL or NOT RUN per audit, and exits non zero if anything failed OR was skipped. `NOT RUN` is never a pass: say which tool was missing.
2. Report the result in plain words: how many packages were scanned by each tool, how many known flaws, and for each flaw the package, the version, how serious, and the fixed version.
3. If everything passes, still say what was NOT covered (the bundled dependencies of vendored files, flaws not yet published, the tools' databases being only as good as their sources).
4. **Make it permanent** (with the owner's yes): copy `assets/audit_workflow.yml` to `.github/workflows/audit.yml`, keep only the steps that apply, pin its actions (`cihardening`), and add the vendored list and test.
   * The workflow also runs every Monday (`schedule`). New flaws are published every week for code that did not change, so a push only workflow goes stale. A failing scheduled run emails the owner: tell them to expect that.
   * The OSV Scanner download is checked against its published SHA 256. Get the value for a version with `scripts/osv_checksum.sh vX.Y.Z` and change the version and the fingerprint together. Honest limit: the fingerprint comes from the same release page, so it catches a damaged or swapped file, not a compromised release.
5. Run the workflow's exact commands locally before pushing. Then, after the push, read the result on the host's Actions page; if you cannot read it, say that you did not see it pass and tell the owner what to look for.
6. Record each audit in the evidence ledger (`guardflow`): outcome, proof (ran, or ran and seen passing in CI), and the limit.

## Reading findings

* A finding is a claim to check, not an order. Look at whether the vulnerable function is actually used (a flaw in a feature the project never calls is lower risk) and whether a fixed version exists.
* Prefer upgrading to the fixed version, then rerun the tests (the `backtest` and `uitests` suites) because an upgrade can change behaviour. Never upgrade a library that produces results without running the backtests.
* If no fix exists, record the finding as open in the ledger with the reason and a review date. Do not silence the scanner.

## Tool notes (learned the hard way)

* `osv-scanner --sbom` is deprecated: pass SBOM files with `-L`.
* pip audit creates a temporary environment to resolve versions; it needs internet and takes a few seconds.
* On a machine behind a proxy, check that the advisory services answer (a request with an empty body should return an error code like 400, not a connection failure).
* Dependabot is a separate, complementary tool: it proposes updates and warns (alerts) about known vulnerable versions. Alerts are a repository setting the owner must switch on (see `ownersteps`).

## Honest limits

A clean audit means no PUBLISHED flaw in the versions it could read. It is not a security review of the libraries, and it says nothing about your own code (see `codescan` and `hostileinput`).
