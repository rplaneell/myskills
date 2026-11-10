#!/usr/bin/env python3
"""Code scan with Semgrep, plus checks so the scanner can never go blind without anyone noticing.

  1. SELF TEST: the rules must fire on a deliberately bad fixture folder, every single rule.
  2. PREPARE (optional): a command that fills the target folder (for example extracting inline scripts from a built page).
  3. REAL SCAN: the target folder is scanned, and the number of files Semgrep actually scanned must equal the number of
     files present. If not, the scan failed silently ("BLIND SCAN") and a result of zero findings would mean nothing.

Report only by default (exit 0 even with findings). --block-errors makes findings of severity ERROR fail the run.

  python3 semgrep_check.py [--rules .semgrep/rules.yml] [--fixtures .semgrep/fixtures] [--target semgrep_input]
                           [--glob '*.js'] [--prepare 'python3 tools/extract.py dist/app.html semgrep_input'] [--block-errors]

Two traps this script exists for (both bit us):
  * Semgrep silently skips folders named build/ and tests/ and files ignored by Git. Keep the target elsewhere.
  * Registry rule sets can load but still miss obvious bad code, and fragments that start with <script> do not parse.
Needs: pip install semgrep   (metrics are switched off, nothing is uploaded)
"""
import argparse, collections, json, pathlib, re, subprocess, sys


def scan(semgrep, rules, target, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [semgrep, "scan", "--metrics=off", "--disable-version-check", "--no-git-ignore", "--config", str(rules), "--json", "-o", str(out), str(target)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not out.exists():
        sys.exit("semgrep did not produce a report:\n" + r.stderr[-800:])
    return json.loads(out.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", default=".semgrep/rules.yml")
    ap.add_argument("--fixtures", default=".semgrep/fixtures")
    ap.add_argument("--target", default="semgrep_input")
    ap.add_argument("--glob", default="*.js", help="which files in the target folder count (default *.js)")
    ap.add_argument("--prepare", help="shell command that fills the target folder before the scan")
    ap.add_argument("--semgrep", default="semgrep")
    ap.add_argument("--workdir", default=".semgrep_work", help="where reports are written (not named build or tests)")
    ap.add_argument("--block-errors", action="store_true")
    a = ap.parse_args()
    rules, target, work = pathlib.Path(a.rules), pathlib.Path(a.target), pathlib.Path(a.workdir)
    if {"build", "tests", "test"} & set(target.parts):
        print(f"WARNING: Semgrep skips folders named build/tests by default; '{target}' may be scanned as zero files.")
    ids = set(re.findall(r"^\s*- id:\s*(\S+)", rules.read_text(), re.M))

    d = scan(a.semgrep, rules, a.fixtures, work / "selftest.json")
    fired = {r["check_id"].split(".")[-1] for r in d["results"]}
    if ids - fired or d["errors"]:
        print("SELF TEST FAILED: the scanner is blind to:", sorted(ids - fired), "| parse errors:", len(d["errors"]))
        return 1
    print(f"self test ok: all {len(ids)} rules fire on the planted bad fixture")

    if a.prepare:
        subprocess.run(a.prepare, shell=True, check=True)
    expected = len(list(target.rglob(a.glob)))
    d = scan(a.semgrep, rules, target, work / "report.json")
    if d["errors"]:
        print("scan had errors, so the result is not trustworthy:", [e.get("message", "")[:80] for e in d["errors"][:3]])
        return 1
    scanned = len(d["paths"]["scanned"])
    if scanned != expected or scanned == 0:
        print(f"BLIND SCAN: {expected} file(s) present but Semgrep scanned {scanned}. A zero result would mean nothing.")
        return 1
    by_rule = collections.Counter(r["check_id"].split(".")[-1] for r in d["results"])
    sev = {r["check_id"].split(".")[-1]: r["extra"]["severity"] for r in d["results"]}
    print(f"scanned {scanned} file(s), {len(d['results'])} finding(s)")
    for rid in sorted(ids):
        print(f"  {rid:32s} {by_rule.get(rid, 0):3d}  {sev.get(rid, '')}")
    errors = sum(n for rid, n in by_rule.items() if sev.get(rid) == "ERROR")
    if a.block_errors and errors:
        print(f"BLOCKING: {errors} finding(s) of severity ERROR")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
