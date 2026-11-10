# How to work on this project

This repository is private and on a plan without branch protection (a paid feature), so GitHub cannot physically stop a bad
push to `main`. These rules plus the automatic checks in `.github/workflows/` take its place.
CI means continuous integration: checks that run automatically on every push.

## The rules

1. **Never work directly on `main`.** Make a branch for each change: `git switch -c fix/short-topic`
2. **One change per branch**, in small commits that each have a clear reason.
3. **Merge into `main` only when every check is green.** Open the Actions tab on GitHub, open your newest run, and look for green
   ticks on all the checks listed below. A red cross or an orange dot means do not merge.
4. **Results never change unless the owner asked for it.** The golden file tests enforce this. If one fails, understand why first.
5. **Edit the sources, never the built file.** Rebuild and commit the built file in the same commit. CI rebuilds and fails if they differ.
6. **Released files are frozen.** Their fingerprints are recorded in a manifest and tested.
7. **No secrets in Git, ever.** Keys, tokens and passwords go only in a local `.env` file. A key that reached GitHub, even briefly, must be revoked and replaced.
8. **Ask first, then act** when working with an assistant: say what will change, wait for a yes.

## Commit messages
First line: a short imperative sentence, at most 72 characters. Then a blank line, then why the change was made and what you checked.

## One time setup
`pip install pre-commit` then `pre-commit install`. This switches on the secret blocker and a hook that refuses `git push` to `main`.

## What the automatic checks catch
| Check | Catches |
|---|---|
| `ci` | build differs from committed output, any failing test, wrong results, coverage below the floor |
| `secret-scan` | keys, tokens or passwords anywhere in Git history |
| `semgrep` | risky code patterns |
| `repo-rules` | tracked secret files, unpinned actions, bad commit messages, oversized files, built file edited without a source change |

These checks tell you after a push. They cannot undo it. The local hooks stop the mistake earlier, but only on computers where the
one time setup was done, and `--no-verify` skips them.
