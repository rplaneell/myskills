# Adoption checklist

Tick each line only when you have SEEN it work. "Should work" is not a tick.

## Phase 0: what is shipped
* [ ] I know which file users run, and how it is built.
* [ ] A fresh build from the sources gives the same fingerprint every time (deterministic build).
* [ ] The shipped file is recorded in a manifest with its SHA 256 fingerprint, or I wrote down that its source is unknown.
* [ ] CI rebuilds and fails if the committed built file differs from a fresh build.

## Phase 1: secrets
* [ ] `.env` and key files are in `.gitignore`; `.env.example` lists names only.
* [ ] The whole Git history was scanned (gitleaks) and the result is written down.
* [ ] A made up fake key is refused by the local commit blocker, and a harmless commit is accepted.
* [ ] CI scans the history on every push; the download of the scanner is checked against a fingerprint.

## Phase 2: backtests
* [ ] Golden files exist for every important scenario, including changed settings, not only defaults.
* [ ] An independent oracle (old trusted version) is compared, with an explicit list of explained differences.
* [ ] A test proves a tiny change (0.001) in a result is noticed.
* [ ] Property tests state rules that hold for every result; two views of one number are compared.
* [ ] I broke a formula in a scratch copy, regenerated golden files, and the property tests or oracle still failed.

## Phase 3: input and clicking
* [ ] Every place where text enters the program is listed and tested with three attack styles.
* [ ] The detector proves it can see a real injection.
* [ ] Clicking tests drive every control like a person; downloads, PDFs and printing are checked by structure.

## Phase 4: coverage
* [ ] Coverage measured twice (to know the wobble); a floor is set a little below the measured value.
* [ ] CI enforces the floor on the FULL run only.

## Phase 5: hardening
* [ ] Every GitHub Action is pinned to a full commit SHA with the tag in a comment.
* [ ] Workflows have least privilege permissions.
* [ ] Dependabot is configured and alerts are switched on.
* [ ] On a plan without branch protection: written rules, a rules check job, and a local push blocker are in place.

## Phase 6: scanning
* [ ] The scanner rules fire on a planted bad file; a BLIND SCAN guard exists.
* [ ] Findings are triaged in writing (real, false alarm, accepted), not ignored.

## Phase 7: mutation checks
* [ ] A list of deliberate breakages of the core calculations was run; survivors each led to a new test or a written reason.

## Phase 8: security checklist
* [ ] Each item of the standard website security list is marked applies, not applicable now, or later.
