---
name: repocontrols
description: Replace paid GitHub protections on a free private repository with written rules, automatic alarms and local hooks. Includes a CONTRIBUTING template, a repo rules checker (tracked secret files, unpinned actions, bad commit messages, oversized files, built file edited without a source change), a local push blocker for main, and an honest table of which protections are paid and what covers each gap. Use when a repository is private on a free plan, when the user asks for branch protection, required checks, or to enforce contribution rules, or to explain what protection a repository really has.
---

# repocontrols: protection without paid features

On a free plan, several GitHub protections need a paid plan for private repositories (this is the situation as we understood it; GitHub changes plans, so tell the owner to confirm on their Settings pages). Typical examples: branch protection and rulesets (refusing a merge unless checks pass), secret scanning with push protection, and CodeQL code scanning. The honest answer is not to pretend they exist. Build free layers and say exactly where they are weaker. See `references/paid_vs_free.md`.

## The layers

1. **Written rules** (`assets/CONTRIBUTING.md`): work on a branch, one change per branch, merge only when every check is green, no secrets, edit sources not built files, results never change unless asked, ask first then act.
2. **An automatic rules check in CI** (`scripts/check_repo_rules.py` plus `assets/repo_rules_workflow.yml`). It fails when:
   * a secret or key file is tracked (`.env`, `.pem`, `.key`, `id_rsa`, `node_modules`, anything you add),
   * a workflow uses an action not pinned to a full commit SHA,
   * a commit message is empty, longer than 72 characters, starts with wip, fixup or squash, or has no blank line after the subject,
   * a file is larger than the limit outside the allowed folders,
   * a built file (for example `dist/`) changed in a push without any source change.
3. **A local push blocker** (`scripts/no_push_to_main.py` plus `assets/pre_commit_pushblocker.yaml`): refuses `git push` to main or master from the owner's computer. An emergency override exists and leaves a trace in the shell history.
4. **Dependabot and alerts** (see `cihardening`).

## Steps (ask before each change to the repository)

1. Ask the plan and visibility. If the repository is public or on a paid plan, tell the owner to use the real protections instead and still keep layers 1 and 2.
2. Copy the files: `check_repo_rules.py` and `no_push_to_main.py` to `tools/`, the workflow to `.github/workflows/repo-rules.yml`, the hook block into `.pre-commit-config.yaml`, `CONTRIBUTING.md` to the root. Optionally `.repo-rules.json` (see `assets/repo_rules.example.json`) for the size limit, the allowed big folders, the built file and what counts as a source change.
3. Pin the checkout action with `cihardening/scripts/pin_actions.py`.
4. Copy `assets/test_repo_rules.py` to the tests and run it: each rule must be able to FAIL. A rule that cannot fail protects nothing. (Tests caught a real bug in the first version: `fixup!` slipped through because a word boundary does not work after an exclamation mark.)
5. Prove it on a throwaway clone: commit a `.env`, an unpinned action, a message "WIP" and a hand edited built file, then run `check_repo_rules.py HEAD~1..HEAD`. All four must be reported, exit code 1.
6. Test the push blocker against a LOCAL fake remote: `git init --bare remote.git`, clone, install the hook, then push to main (must be refused, nothing reaches the remote), push a feature branch (accepted), push with the override (accepted). Use a clean remote and a NEW commit: leftover remote tracking references in a test clone make `pre-commit` skip push hooks, which looks like a failure of the hook but is a flaw in the test setup.
7. Test the range logic of the workflow for a new branch, a force push (the "before" commit no longer exists) and a normal push; the fallback is everything not yet on main.

## Honest limits to tell the owner

* Nothing can physically stop a push to main on a plan without branch protection. The CI job tells you AFTER the push; the local hook helps only where `pre-commit install` was run and `--no-verify` skips it.
* There is no required review when one person owns the repository. Tests and checks stand in for review.
* The rules job is only as good as its rules. Review them when the project changes.

## What the owner must click themselves

* Settings, Code security: switch on Dependabot alerts. Check there whether secret scanning or code scanning are offered; if not, nothing is lost, the layers above are in place.
* On every computer used to commit: `pip install pre-commit`, then `pre-commit install`.
* After each push: Actions tab, newest run, green ticks.

If the repository ever becomes public or moves to a paid plan, switch on the real protections and keep these layers as a second line.
