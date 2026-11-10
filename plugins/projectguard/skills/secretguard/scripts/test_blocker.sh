#!/usr/bin/env bash
# Prove the local secret blocker works, in a THROWAWAY repository (your real project is never touched).
# It makes up a fake GitHub style token at run time (random characters, never a real key), tries to commit it, and expects
# the commit to be REFUSED; then it commits a harmless file and expects that to be ACCEPTED.
# Usage: ./test_blocker.sh path/to/.pre-commit-config.yaml     Needs: git, python3, pre-commit installed.
set -uo pipefail
cfg="$(cd "$(dirname "${1:?usage: test_blocker.sh path/to/.pre-commit-config.yaml}")" && pwd)/$(basename "$1")"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cd "$tmp" && git init -q && git config user.email t@example.invalid && git config user.name t
cp "$cfg" .pre-commit-config.yaml && pre-commit install >/dev/null
python3 - <<'PY'
import random, string
r = random.SystemRandom()
open("fake_config.py", "w").write('TOKEN = "ghp_' + "".join(r.choice(string.ascii_letters + string.digits) for _ in range(36)) + '"\n')
PY
git add fake_config.py
if git commit -q -m "try a fake key" >/dev/null 2>&1; then echo "FAIL: the commit with a fake key was ACCEPTED"; exit 1; fi
echo "ok: the commit with a fake key was refused"
git rm -q --cached fake_config.py; rm fake_config.py; echo "harmless note" > note.txt; git add note.txt
if git commit -q -m "harmless" >/dev/null 2>&1; then echo "ok: a harmless commit was accepted"; else echo "FAIL: a harmless commit was refused"; exit 1; fi
