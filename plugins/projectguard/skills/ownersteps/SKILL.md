---
name: ownersteps
description: Handle the protections only the owner can switch on, because the assistant works in a cloud container and cannot touch the owner's computer or account settings. Covers a cross platform checker the owner runs to see which local protections are really on (pre commit hooks, push blocker, ignore rules, identity), exact steps for Windows, macOS and Linux, click paths for GitHub repository settings such as Dependabot alerts, how to record an owner reported action honestly, and how to explain it without blame. Use when a protection needs the owner's computer or an account setting, when asked to install hooks or switch on alerts, or when verifying that setup instructions were really followed.
---

# ownersteps: the part only you can do

Some protections live where an assistant cannot reach: the owner's computer (hooks that run when they commit), and account settings (alerts, branch rules). Pretending otherwise gives false confidence. This skill makes those steps small, exact, verifiable and honestly recorded.

## What the assistant can and cannot do

* **Can:** write the config files into the repository, write the steps, write a checker, test the protections in a throwaway repository, read CI results through a connected tool.
* **Cannot:** install anything on the owner's computer, click settings in their account, or confirm that a setting is on. If a tool shows no way to read a setting, say so.
* **Never:** claim a protection is active because the file exists. A hook file in the repository does nothing until `pre-commit install` was run on each computer.

## The checker

Give the owner `scripts/check_setup.py`. Run inside the project folder, on Windows, macOS or Linux:

```
python check_setup.py
```

It prints DONE or NOT DONE for each local protection and the exact fix in plain words, changes nothing, and exits non zero until everything is done: the `pre-commit` program installed, the config file present, the commit blocker hook installed, the push blocker hook installed, `.env` ignored and not tracked, and Git knowing who the committer is. After the fixes, ask them to run it again and paste the output.

## The commands, by system

* **Windows (PowerShell):** `py -m pip install pre-commit` then `pre-commit install` (if `pre-commit` is not found, use `py -m pre_commit install`). If the hook says `python3` is not found, change `python3` to `python` in the push blocker entry of `.pre-commit-config.yaml`.
* **macOS and Linux:** `pip install pre-commit` (or `pipx install pre-commit`) then `pre-commit install`.
* Run `pre-commit install` once in each project folder and on each computer used to commit.
* First run downloads the scanner, so internet is needed once. Test with `pre-commit run --all-files`.

## GitHub settings (say they may be named differently; screens change)

* **Dependabot alerts:** repository, Settings, Code security (named Advanced Security on some accounts), Dependabot alerts, Enable. Free on private repositories. Dependabot version updates are configured by a file in the repository and are separate.
* **Secret scanning, push protection, branch protection, code scanning:** paid for private repositories on a free plan; check the same page whether they are offered. Do not tell the owner to look for what is not there.
* **After a push:** the Actions tab, newest run, green ticks on every workflow.

## Recording an owner action honestly

When the owner says "it is on", record it as reported by the owner, not as verified: outcome clean only with proof `ran` if you saw the checker output, and put "reported by the owner, not verifiable from here" in the detail otherwise. Prefer asking for the checker output or a screenshot of the setting over taking it on trust, and never ask for a screenshot that shows a secret.

## How to ask (tone)

Plain words, no blame, the reason first ("the commit blocker only works on a computer where this was run"), then the one or two commands, then how to check. Offer to wait while they do it. Keep the list short: the high priority items first.

## Honest limits

* A checker run on the owner's computer proves that computer, not others.
* `git commit --no-verify` and `git push --no-verify` skip the hooks. The CI layers (secret scan, rules job) are the second line; say so.
