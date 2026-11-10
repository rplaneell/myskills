#!/usr/bin/env python3
"""Fingerprints (SHA 256) for released files, so any later change to a release is caught by a test.

  python3 release_manifest.py write     records NEW release files only; files already recorded are never rewritten
  python3 release_manifest.py verify    exit 1 if a recorded file changed, is missing, or a release file is not recorded

Options: --dir releases   --glob '*.html'   --manifest MANIFEST.json (inside --dir)
The manifest also records the commit that added each file and says honestly when the build source is unknown.
Limits: a fingerprint proves the file did not change since it was recorded. It does not prove what it was built from.
"""
import argparse, hashlib, json, pathlib, subprocess, sys


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def added_in(p):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", str(p)], capture_output=True, text=True).stdout.split()
    return out[-1] if out else "uncommitted"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["write", "verify"])
    ap.add_argument("--dir", default="releases")
    ap.add_argument("--glob", default="*")
    ap.add_argument("--manifest", default="MANIFEST.json")
    a = ap.parse_args()
    rel = pathlib.Path(a.dir)
    manifest = rel / a.manifest
    files = sorted(p for p in rel.glob(a.glob) if p.is_file() and p.name != a.manifest)
    if a.command == "write":
        rec = json.loads(manifest.read_text()) if manifest.exists() else {"files": {}}
        for p in files:
            if p.name not in rec["files"]:
                rec["files"][p.name] = {"sha256": sha256(p), "bytes": p.stat().st_size, "added_in_commit": added_in(p),
                                        "built_from": "unknown: recorded after the fact; fill in the source commit when it is known"}
        manifest.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    rec = json.loads(manifest.read_text())["files"]
    present = {p.name: p for p in files}
    bad = [f"changed: {n}" for n, p in present.items() if n in rec and sha256(p) != rec[n]["sha256"]]
    bad += [f"not recorded: {n}" for n in present if n not in rec]
    bad += [f"missing: {n}" for n in rec if n not in present]
    for b in bad:
        print(b)
    print(f"{len(rec)} recorded, {len(present)} present, {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
