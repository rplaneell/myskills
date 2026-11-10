#!/usr/bin/env python3
"""Mutation check: break the code on purpose, one small way at a time, and see whether the tests notice.

A mutant is a small deliberate mistake (a plus turned into a minus, a limit changed, a check removed).
If the tests FAIL, the mutant is CAUGHT (good). If the tests still PASS, it SURVIVED: no test notices that mistake, so a
real bug of that kind would slip through. Survivors are the useful result: each one points at a missing test.

  python3 mutate.py spec.json [--project .] [--only NAME] [--exclude releases --exclude data] [--allow-survivors]

spec.json:
  {"test_command": "python3 -m pytest tests -q -x",      what to run in the copy; exit code 0 means "tests pass"
   "timeout": 900,                                        seconds per run (a timeout counts as caught: a hang is noticed)
   "mutants": [ {"name": "zoom factor 0.7 instead of 0.6", "file": "dist/app.html",
                 "old": "zoomAround(0.6)", "new": "zoomAround(0.7)"} ]}

Your real files are never touched: everything runs in a temporary copy of the project.
Each "old" text must occur exactly once in its file, otherwise the mutant is rejected (it would prove nothing).
Edit the SOURCE and rebuild if your tests run against a built file: mutate the file the tests really use.
Cost: one full test run per mutant, so keep test_command focused (a few seconds to a minute).
"""
import argparse, json, pathlib, shutil, subprocess, sys, tempfile, time

DEFAULT_EXCLUDE = [".git", "node_modules", "__pycache__", ".venv", ".pytest_cache"]


def run(cmd, cwd, timeout):
    t = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)[-600:], time.time() - t
    except subprocess.TimeoutExpired:
        return 124, "timed out", time.time() - t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--project", default=".")
    ap.add_argument("--only")
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--allow-survivors", action="store_true")
    a = ap.parse_args()
    spec = json.loads(pathlib.Path(a.spec).read_text())
    src = pathlib.Path(a.project).resolve()
    timeout = spec.get("timeout", 900)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="mutate_"))
    work = tmp / "project"
    shutil.copytree(src, work, ignore=shutil.ignore_patterns(*(DEFAULT_EXCLUDE + a.exclude)))
    try:
        code, tail, secs = run(spec["test_command"], work, timeout)
        if code != 0:
            print(f"BASELINE FAILS: the tests do not pass on the unbroken code, so no mutant result would mean anything.\n{tail}")
            return 2
        print(f"baseline ok ({secs:.0f}s per run). {len(spec['mutants'])} mutant(s):\n")
        survivors, rejected = [], []
        for m in spec["mutants"]:
            if a.only and a.only != m["name"]:
                continue
            target = work / m["file"]
            original = (src / m["file"]).read_text(encoding="utf-8")
            n = original.count(m["old"])
            if n != 1:
                print(f"REJECTED  {m['name']}: the text to change occurs {n} times (must be exactly 1)")
                rejected.append(m["name"])
                continue
            target.write_text(original.replace(m["old"], m["new"]), encoding="utf-8")
            code, tail, secs = run(spec["test_command"], work, timeout)
            target.write_text(original, encoding="utf-8")
            status = "CAUGHT  " if code != 0 else "SURVIVED"
            print(f"{status}  {m['name']}  ({secs:.0f}s)")
            if code == 0:
                survivors.append(m["name"])
        total = len([m for m in spec["mutants"] if not a.only or a.only == m["name"]])
        print(f"\n{total - len(survivors) - len(rejected)} of {total} caught, {len(survivors)} survived, {len(rejected)} rejected.")
        for s in survivors:
            print("  needs a test:", s)
        for s in rejected:
            print("  fix the spec (text not found exactly once):", s)
        return 0 if (not survivors and not rejected or a.allow_survivors) else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
