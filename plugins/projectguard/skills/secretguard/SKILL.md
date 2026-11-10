---
name: secretguard
description: Keep API keys, tokens and passwords out of Git, in layers. Covers the .env and .gitignore rules, scanning the whole Git history with gitleaks, a local pre commit blocker that refuses a commit containing a secret, a CI scan on every push with a fingerprint checked download, how to test the blocker with a made up fake key, and what to do after a leak. Use when starting or auditing any project, when secrets might be in the code, or when the user asks to hide API keys, check environment variables or check the Git history for keys.
---

# secretguard: stop secrets reaching Git

A secret is a key, token or password. If one reaches GitHub, bots can find it within seconds, and Git remembers everything forever, so deleting the commit does not help. The only safe approach is to stop it before it is ever saved, and to have a second layer that notices if the first one was skipped.

## The layers

1. **A rule and a habit:** secrets live only in a local `.env` file that Git never sees. `.env` is in `.gitignore`. A file `.env.example` lists the variable NAMES with empty values, so others know what to set.
2. **A history scan:** run gitleaks over every commit ever made, once now, and write down the result.
3. **A local blocker:** a pre commit hook (a small check that runs on your computer just before each commit is saved) that refuses any commit containing a secret.
4. **A CI scan:** the same scanner on every push, over the whole history, so a skipped hook is still noticed.

## Steps (ask the owner before each change to their repository)

1. **Check the rule first.** Tell the owner if anything breaks it: a tracked `.env`, keys in source, docs, screenshots or commit messages.
2. **Add the ignore rules.** Append `assets/gitignore_snippet.txt` to `.gitignore`. Add `assets/env.example` as `.env.example` (names only). Confirm with `git check-ignore -v .env .env.local .env.example`: the first two are ignored, the example is not.
3. **Scan the history.** Download gitleaks (a program that searches text for secrets), run `gitleaks git --no-banner --redact -v .`, and report: number of commits scanned and "no leaks found" or each finding. Never print a real secret into the chat; use `--redact`.
4. **Install the local blocker.** Copy `assets/pre_commit_config.yaml` to `.pre-commit-config.yaml`. The owner runs `pip install pre-commit` and then `pre-commit install` on every computer they commit from. Say clearly that you did not install the hook on their computer.
5. **Prove the blocker works** with `scripts/test_blocker.sh path/to/.pre-commit-config.yaml`. It makes a throwaway repository, invents a fake token at run time (random characters, never a real key), expects the commit to be REFUSED, and expects a harmless commit to be ACCEPTED. Report both results.
6. **Add the CI scan.** Copy `assets/secrets_workflow.yml` to `.github/workflows/secrets.yml`. It downloads gitleaks and checks the download against a SHA 256 fingerprint (a unique code of the file). To change the version, run `scripts/gitleaks_checksum.sh NEW_VERSION` and change the version and the fingerprint together. Pin the checkout action with `cihardening/scripts/pin_actions.py`.
7. **Write a short setup guide** for the project (`docs/SECRETS_SETUP.md`): the two install commands, what to do when a commit is blocked (move the value to `.env`), what a `gitleaks:allow` comment is for (a false alarm, with a reason), and the leak procedure below.

## If a secret ever reached GitHub

Treat it as stolen, even if you deleted the commit. Revoke it at the provider that issued it and make a new one. Then, if the owner wants, clean the history (a rewrite plus a force push, which needs a safety copy and an explicit yes). Check the provider's logs for use of the old key. See `references/leak_response.md`.

## Honest limits to tell the owner

* The local hook only protects computers where `pre-commit install` was run, and `git commit --no-verify` skips it. The CI scan is the second layer, and it only notices AFTER the secret reached GitHub.
* GitHub's own secret scanning and push protection (which would block the push itself) are paid features for private repositories. Do not rely on them without checking the plan. On a public repository they are free; switch them on.
* A fingerprint taken from the same release page as the download catches a damaged or swapped file, not a compromised release.
* Scanners miss secrets with unusual formats. Do not paste real secrets anywhere to test; use the made up token.

## Quick commands

```
git check-ignore -v .env .env.local .env.example
gitleaks git --no-banner --redact -v .
scripts/test_blocker.sh .pre-commit-config.yaml
scripts/gitleaks_checksum.sh 8.30.1
```
