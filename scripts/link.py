#!/usr/bin/env python3
"""Link a project to the myskills marketplace.

Usage:
  python3 scripts/link.py PROJECT_FOLDER [plugin ...]     e.g.  link.py ~/proj frontend impeccable
  python3 scripts/link.py --user [plugin ...]             link EVERY project on this computer

Always adds the always on set (core, superpowers, task-observer) plus any plugins you name.
Existing settings in the file are kept.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "rplaneell/myskills"
ALWAYS = ["core", "superpowers", "task-observer"]

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
if args[0] == "--user":
    target = Path.home() / ".claude" / "settings.json"
    names = args[1:]
else:
    target = Path(args[0]).expanduser() / ".claude" / "settings.json"
    names = args[1:]
known = {p["name"] for p in json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())["plugins"]}
bad = [n for n in names if n not in known]
if bad:
    sys.exit(f"unknown plugin(s): {', '.join(bad)}\nchoose from: {', '.join(sorted(known))}")
target.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(target.read_text()) if target.exists() else {}
data.setdefault("extraKnownMarketplaces", {})["myskills"] = {"source": {"source": "github", "repo": REPO}}
enabled = data.setdefault("enabledPlugins", {})
for n in ALWAYS + names:
    enabled[f"{n}@myskills"] = True
target.write_text(json.dumps(data, indent=2) + "\n")
print(f"wrote {target}")
print("enabled:", ", ".join(k for k, v in enabled.items() if v))
