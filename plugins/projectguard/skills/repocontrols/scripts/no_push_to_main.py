#!/usr/bin/env python3
"""Local pre push hook: refuse a push that updates main or master from this computer.

pre-commit gives the branch being pushed to in PRE_COMMIT_REMOTE_BRANCH (for example refs/heads/main).
Emergency override, visible in your shell history:  PQ_ALLOW_MAIN_PUSH=1 git push
Limits: only works where `pre-commit install` was run, and `git push --no-verify` skips it. It is a safety belt, not a lock.
"""
import os, sys

branch = os.environ.get("PRE_COMMIT_REMOTE_BRANCH", "")
name = branch.removeprefix("refs/heads/")
if name in ("main", "master") and os.environ.get("PQ_ALLOW_MAIN_PUSH") != "1":
    print(f"BLOCKED: pushing straight to '{name}' is against the repository rules.\n"
          f"Push a branch and merge it when every check is green.\n"
          f"(Emergency only: PQ_ALLOW_MAIN_PUSH=1 git push ...)")
    sys.exit(1)
