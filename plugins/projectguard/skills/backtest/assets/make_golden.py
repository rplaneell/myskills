#!/usr/bin/env python3
"""Regenerate golden files ON PURPOSE. Never run automatically, never to turn a red test green without understanding why.

  python3 make_golden.py current     writes golden/current/*.txt from the build under test
  python3 make_golden.py oracle      writes golden/oracle/*.txt from the frozen release (refuses if its fingerprint changed)

Changing a golden file means a result changed. Do it only when the owner asked for it, keep the diff in the same commit as the
change, and say in the commit message which numbers moved and why.
"""
import hashlib, json, pathlib, sys
from golden_lib import GOLDEN, SCENARIOS, export_text

BUILD = "path/or/url/of/the/build/under/test"          # FILL IN
ORACLE_BUILD = "releases/the_trusted_old_release"       # FILL IN
MANIFEST = pathlib.Path("releases/MANIFEST.json")


def main(which):
    if which == "current":
        build, out = BUILD, GOLDEN / "current"
    elif which == "oracle":
        build, out = ORACLE_BUILD, GOLDEN / "oracle"
        name = pathlib.Path(build).name
        want = json.loads(MANIFEST.read_text())["files"][name]["sha256"]
        got = hashlib.sha256(pathlib.Path(build).read_bytes()).hexdigest()
        if got != want:
            sys.exit(f"refusing: the oracle release {name} no longer matches its recorded fingerprint")
        out.mkdir(parents=True, exist_ok=True)
        (out / "SOURCE.json").write_text(json.dumps({"release": name, "sha256": want}, indent=2) + "\n")
    else:
        sys.exit(__doc__)
    out.mkdir(parents=True, exist_ok=True)
    for name, scenario in SCENARIOS.items():
        (out / f"{name}.txt").write_text(export_text(build, scenario), encoding="utf-8", newline="\n")
        print("wrote", out / f"{name}.txt")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
