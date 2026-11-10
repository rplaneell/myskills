---
name: releaseintegrity
description: Make releases traceable. Find out what the shipped file was really built from, rebuild deterministically, record SHA 256 fingerprints of released files in a manifest and test them, compare a shipped file with a fresh build, make CI fail when the committed build output differs from a rebuild, and tag releases. Use when starting on a project that ships a built file or releases, when "which code produced this file" matters, when releases live in a folder without a recorded source, or when the user asks for traceability.
---

# releaseintegrity: prove which code produced which file

Traceability means: for any file a user runs, you can name the exact commit it was built from and prove it. Many projects cannot. Find out first, before testing anything else, because tests on the wrong file protect nothing.

## Phase 0: what is really shipped?

1. Ask which file users run and how it was made.
2. Build the project from the sources in a scratch copy and compare with the shipped file: `scripts/compare_builds.py shipped fresh`. Look at size, SHA 256 fingerprint, number and size of inline scripts, embedded data. A very different script count or size means the shipped file contains code the sources do not produce (older, newer, or from another place). In our case the file the lab used was three times larger than the build of the repository's sources and had features the sources lacked.
3. Check the build is deterministic: build twice (and in a clean clone); the fingerprint must be identical. If not, find the cause (timestamps, random ids, unsorted data) and fix it.
4. Tell the owner plainly what you found, before changing anything.

## Freeze what exists

`scripts/release_manifest.py write --dir releases --glob '*.html'` records, for each released file: SHA 256 fingerprint, size, the commit that added it, and "built from: unknown" when that is the truth. Recorded entries are never rewritten. `verify` exits 1 if a recorded file changed, is missing, or a release file is not recorded. Add a test that runs `verify`, and prove it by changing one byte in a scratch copy.

A frozen release is then usable as an ORACLE for backtests (see `backtest`): its outputs on known inputs are the answer key against which new builds are compared.

## Make new builds traceable

1. **Rebuild check in CI:** build, then `git diff --exit-code -- dist/`. The committed built file must equal a fresh build.
2. **Embed the version and commit** in the built file (shown in an About or footer) so a user can tell what they have.
3. **Tag releases** (`v1.2.3`) and record the fingerprint of the released file in the manifest at that tag.
4. **One command rebuilds a past release** from its tag, and the fingerprint matches. Practise it once; write the command in the docs.
5. Never edit built files by hand; edit sources and rebuild (the `repocontrols` rules job flags a built file changing without a source change).

## The decision about an old shipped file that the sources cannot rebuild

Offer the owner these options and recommend a blend: (a) freeze it, fingerprint it, and use it as the oracle; (b) port its missing features into the sources step by step, checking each step against the oracle; (c) declare the rebuilt output the product and retire the old file. Do not decide for them.

## Honest limits

* A fingerprint proves a file did not change after it was recorded. It does not prove what it was built from.
* Matching size and script counts is evidence, not proof. The proof is rebuilding from a tagged commit and getting the same fingerprint.
* If a build embeds a timestamp, determinism fails; remove it or inject it from the commit date.

## Files
* `scripts/release_manifest.py`, `scripts/compare_builds.py`
