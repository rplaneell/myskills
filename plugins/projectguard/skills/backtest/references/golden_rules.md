# Rules for golden files

1. **A golden file is evidence, not a convenience.** It records what the owner accepted. Changing it is a decision, not a chore.
2. **Generate on purpose.** `make_golden.py` is never run by CI and never run just to make a test pass.
3. **One reason per change.** A commit that changes golden files should contain the code change that caused it and nothing unrelated.
4. **Read the diff.** Before committing regenerated files, read every changed line and be able to explain it.
5. **Determinism first.** Run the generation twice. If the files differ, find the cause (timestamps, random order, unsorted sets, locale) and fix it or normalize it by a named pattern. Do not loosen the comparison.
6. **Keep the allowlist tiny and explained.** Each line allowed to differ from the oracle needs a comment saying why, and a test that pins the exact set, so adding to it forces a conscious edit.
7. **Cover the settings, not only the defaults.** For every control a person can change, one scenario. For every input type, one messy example and one empty/nothing detected example.
8. **A scenario must change something.** Test that each variant differs from its base (or equals it where it must, such as a display language).
9. **Store the oracle's identity.** `SOURCE.json` with the release name and SHA 256 fingerprint, tied to the release manifest, so nobody can swap the oracle files unnoticed.
10. **Never put real secrets or private data into golden files.** Use synthetic example data.

## Exploring an oracle (before writing the allowlist)

For each scenario, run both versions and print the differing lines. Group the differences by their first field. Expect a handful of families (a setting that exists only in the old version, a value derived from a feature that was reimplemented, a timestamp). Understand each family before allowing it. If a difference touches a headline number, stop: that is either a bug or a decision the owner must make.

## Layout

```
tests/
  golden_lib.py          scenarios, volatile patterns, known differences, how to run one scenario
  test_golden.py         the comparisons and the sensitivity checks
  make_golden.py         regeneration (manual)
  golden/
    current/<name>.txt
    oracle/<name>.txt
    oracle/SOURCE.json
```
