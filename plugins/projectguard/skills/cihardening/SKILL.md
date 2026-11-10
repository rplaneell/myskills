---
name: cihardening
description: Harden GitHub Actions and the build pipeline. Pin every action to a full commit SHA with a script that resolves tags, give workflows least privilege permissions, check downloaded tools against SHA 256 fingerprints, configure Dependabot for npm, pip and Actions, make CI rebuild the committed build output and fail on a difference, and keep CI time and cost in mind. Use when setting up or reviewing CI, when the user asks to protect against supply chain attacks, pin dependencies, add Dependabot, or secure GitHub workflows.
---

# cihardening: make the automation itself safe

CI (continuous integration) runs code from other people on every push. If that code changes under your feet, an attacker or a mistake can run anything in your pipeline. These steps shrink that risk and make the pipeline traceable.

## 1. Pin every action to a full commit SHA

A version tag such as `v4` can be moved to different code at any time. A full commit SHA (a 40 character fingerprint of the code) cannot. Pin like this, keeping the readable version as a comment:

```
- uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
```

Use `scripts/pin_actions.py`:

```
python3 pin_actions.py                 # check only, exit 1 if anything is unpinned
python3 pin_actions.py --write --newest   # pin; a bare major tag like v4 becomes the newest v4.x.y release
```

It asks GitHub with `git ls-remote` (annotated tags have a peeled line that holds the real commit; the script handles that). Test it by running the check on an unpinned scratch workflow, pinning, then checking again. Then let `repocontrols` enforce it forever (its rules job fails on an unpinned action).

Honest limit: pinning protects against FUTURE changes. If the tag was already tampered with before you pinned, you pinned the bad code.

## 2. Least privilege

Start every workflow with `permissions: contents: read`. Add more only for a job that needs it, and say why in a comment. Never use `pull_request_target` with untrusted code.

## 3. Downloads must be checked

When a workflow downloads a tool, compare the file with a known SHA 256 fingerprint and stop if it differs (`echo "<sha>  file" | sha256sum -c -`). Take the fingerprint from the publisher's checksums file. Change the version and the fingerprint together. Honest limit: a fingerprint from the same release page catches a damaged or swapped file, not a compromised release.

## 4. The build must be reproducible and checked

If the repository commits a built file (for example `dist/`), CI must rebuild and fail on any difference:

```
python3 build.py
git diff --exit-code -- dist/
```

That proves the committed file really comes from the committed sources. If the build is not deterministic (timestamps, random ids), fix that first, otherwise this check is noise.

## 5. Dependabot

Copy `assets/dependabot.yml`, keep only the ecosystems the project uses (npm, pip, `github-actions`), weekly, a small limit of open pull requests. Dependabot never merges anything. Separately, the owner switches on Dependabot ALERTS under Settings, Code security (free on private repositories); the version updates and the alerts are different switches. Anything Dependabot cannot see (a tool version written in a script, a pre commit hook version) needs a reminder in the docs.

## 6. Cost and time

On a free private plan, Actions minutes are limited per month. A browser test job can take five minutes. Keep fast checks (secret scan, rules, scanner) as separate small workflows, run the slow test job once per push, and avoid triggering it for documentation only changes if the owner wants to save minutes (`paths-ignore`).

## 7. Reading the results

If you can read the Actions results through a connected tool, report the conclusion of each workflow for the newest commit and say which were still running. If you cannot, give the owner the exact thing to look for: the Actions tab, the newest run, green ticks on every workflow. Never say a run passed unless you saw it.

## Checklist

* [ ] `pin_actions.py` check passes
* [ ] every workflow has `permissions`
* [ ] every download is fingerprint checked
* [ ] rebuild equals committed output
* [ ] Dependabot file present, alerts switched on by the owner

See `assets/ci_workflow_example.yml` for a complete hardened example.
