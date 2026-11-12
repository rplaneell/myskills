#!/usr/bin/env bash
# Run every dependency audit that applies to a project, in a scratch COPY of the lock files (nothing in the project is changed).
# Usage: run_audits.sh [project_dir]       Environment: PIP_AUDIT=/path/to/pip-audit  OSV_SCANNER=/path/to/osv-scanner
# Each audit prints one line: PASS, FAIL (with the tool output) or NOT RUN (tool or file missing). NOT RUN is never a pass.
# Exit code 0 only if nothing failed AND nothing was skipped for a missing tool.
set -uo pipefail
proj="$(cd "${1:-.}" && pwd)"; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
pipaudit="${PIP_AUDIT:-pip-audit}"; osv="${OSV_SCANNER:-osv-scanner}"; fail=0; skipped=0
say() { printf '%-34s %s\n' "$1" "$2"; }

if [ -f "$proj/package-lock.json" ]; then
  cp "$proj/package.json" "$proj/package-lock.json" "$tmp/" 2>/dev/null
  if command -v npm >/dev/null; then
    if (cd "$tmp" && npm audit --audit-level=low >npm.out 2>&1); then say "npm audit" "PASS"; else say "npm audit" "FAIL"; sed 's/^/    /' "$tmp/npm.out" | head -20; fail=1; fi
  else say "npm audit" "NOT RUN (npm missing)"; skipped=1; fi
else say "npm audit" "NOT RUN (no package-lock.json)"; fi

reqs=$(ls "$proj"/requirements*.txt 2>/dev/null | head -5)
if [ -n "$reqs" ]; then
  if command -v "$pipaudit" >/dev/null 2>&1; then
    for r in $reqs; do
      if "$pipaudit" -r "$r" --progress-spinner off >"$tmp/pip.out" 2>&1; then say "pip audit $(basename "$r")" "PASS"; else say "pip audit $(basename "$r")" "FAIL"; sed 's/^/    /' "$tmp/pip.out" | head -20; fail=1; fi
    done
  else say "pip audit" "NOT RUN (pip-audit missing: pip install pip-audit)"; skipped=1; fi
else say "pip audit" "NOT RUN (no requirements*.txt)"; fi

args=(); for f in package-lock.json requirements.txt sbom/vendored.cdx.json poetry.lock Cargo.lock go.mod pnpm-lock.yaml yarn.lock; do [ -f "$proj/$f" ] && args+=(-L "$proj/$f"); done
if [ ${#args[@]} -gt 0 ]; then
  if command -v "$osv" >/dev/null 2>&1; then
    if "$osv" scan source "${args[@]}" >"$tmp/osv.out" 2>&1; then say "OSV Scanner" "PASS ($(grep -c 'Scanned' "$tmp/osv.out") files)"; else say "OSV Scanner" "FAIL"; sed 's/^/    /' "$tmp/osv.out" | tail -25; fail=1; fi
  else say "OSV Scanner" "NOT RUN (osv-scanner missing)"; skipped=1; fi
else say "OSV Scanner" "NOT RUN (no lock file or SBOM found)"; fi
[ -f "$proj/sbom/vendored.cdx.json" ] || echo "note: no sbom/vendored.cdx.json. Libraries copied into the project (vendored) are invisible to every audit above."
[ $fail -eq 0 ] && [ $skipped -eq 0 ]
