#!/usr/bin/env python3
"""Manage the myskills marketplace.

Commands:
  add SRC --group G [--always]   copy a skill folder in (SRC = local folder, or owner/repo[/subpath] on GitHub)
  promote NAME                   move a skill into the always on plugin (core)
  demote NAME --group G          move a skill out of core into another group
  add-plugin NAME --repo owner/repo [--path sub] --tier always|project|local --desc TEXT\n                                 register a ready made plugin from GitHub (no copying)\n  list                           show every group and skill
  build                          regenerate marketplace.json and check every skill
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
MARKET = ROOT / ".claude-plugin" / "marketplace.json"
MARKET_NAME = "myskills"
OWNER = "rplaneell"
IGNORE = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "node_modules", ".env", ".DS_Store")


EXTERNAL = ROOT / "external.json"
TIERS = {"always": "[ALWAYS ON] ", "project": "[PER PROJECT] ", "local": "[LOCAL MACHINE ONLY] "}


def load_external():
    return json.loads(EXTERNAL.read_text())["plugins"] if EXTERNAL.exists() else []


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if k.strip() in ("name", "description") and v.strip():
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def skill_dirs(group: Path):
    base = group / "skills"
    return sorted(p for p in base.iterdir() if (p / "SKILL.md").exists()) if base.exists() else []


def find_skill(name: str):
    for g in sorted(PLUGINS.iterdir()):
        d = g / "skills" / name
        if d.exists():
            return g, d
    sys.exit(f"skill '{name}' not found")


def ensure_plugin(group: str, description: str = ""):
    g = PLUGINS / group
    (g / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (g / "skills").mkdir(exist_ok=True)
    pj = g / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        pj.write_text(json.dumps({"name": group, "description": description or f"{group} skills", "version": "1.0.0", "author": {"name": OWNER}}, indent=2) + "\n")
    return g


def build():
    problems = []
    plugins = []
    seen = {}
    for g in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        pj = json.loads((g / ".claude-plugin" / "plugin.json").read_text())
        for s in skill_dirs(g):
            fm = frontmatter(s / "SKILL.md")
            if "name" not in fm or "description" not in fm:
                problems.append(f"missing name/description: {s.relative_to(ROOT)}")
            if s.name in seen:
                problems.append(f"duplicate skill name '{s.name}' in {g.name} and {seen[s.name]}")
            seen[s.name] = g.name
        tag = "[ALWAYS ON] " if g.name == "core" else "[PER PROJECT] "
        plugins.append({"name": pj["name"], "source": f"./plugins/{g.name}", "description": tag + pj["description"]})
    for e in load_external():
        tag = TIERS[e["tier"]]
        plugins.append({"name": e["name"], "source": e["source"], "description": tag + e["description"]})
    MARKET.write_text(json.dumps({"name": MARKET_NAME, "description": "Personal skills and plugins marketplace", "owner": {"name": OWNER}, "plugins": plugins}, indent=2) + "\n")
    # core: write the always on reminder that a session start hook prints
    core = PLUGINS / "core"
    if core.exists():
        lines = ["ALWAYS USE these skills when they apply (they come from the core plugin of the myskills marketplace):"]
        for e in load_external():
            if e["tier"] == "always":
                lines.append(f"- plugin {e['name']}: {e['description'][:200]}")
        for s in skill_dirs(core):
            lines.append(f"- {s.name}: {frontmatter(s / 'SKILL.md').get('description', '')[:200]}")
        (core / "ALWAYS.md").write_text("\n".join(lines) + "\n")
    # always.txt: the plugins every online session installs at start up (read by the environment setup script)
    always = (["core"] if (PLUGINS / "core").exists() else []) + [e["name"] for e in load_external() if e["tier"] == "always"]
    (ROOT / "always.txt").write_text("\n".join(always) + "\n")
    for p in problems:
        print("PROBLEM:", p)
    print(f"built {len(plugins)} plugins, {len(seen)} skills")
    return not problems


def fetch(src: str) -> Path:
    p = Path(src).expanduser()
    if p.exists():
        return p
    parts = src.replace("https://github.com/", "").strip("/").split("/")
    repo = "/".join(parts[:2])
    sub = "/".join(parts[2:])
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{repo}", str(tmp / "r")], check=True)
    return tmp / "r" / sub if sub else tmp / "r"


def add(src, group, always):
    s = fetch(src)
    if not (s / "SKILL.md").exists():
        sys.exit(f"no SKILL.md in {s}. Point at the skill folder itself.")
    fm = frontmatter(s / "SKILL.md")
    name = fm.get("name") or s.name
    group = "core" if always else group
    if not group:
        sys.exit("give --group or --always")
    g = ensure_plugin(group)
    dest = g / "skills" / (name if name != "" else s.name)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(s, dest, ignore=IGNORE)
    build()
    print(f"added {name} to {group}")


def add_plugin(name, repo, path, tier, desc):
    src = {"source": "github", "repo": repo} if not path else {"source": "git-subdir", "url": f"https://github.com/{repo}.git", "path": path}
    data = {"plugins": [e for e in load_external() if e["name"] != name]}
    data["plugins"].append({"name": name, "source": src, "description": desc, "tier": tier})
    EXTERNAL.write_text(json.dumps(data, indent=2) + "\n")
    build()
    print(f"registered plugin {name} ({tier})")


def move(name, group):
    g, d = find_skill(name)
    ensure_plugin(group)
    shutil.move(str(d), str(PLUGINS / group / "skills" / name))
    build()
    print(f"moved {name} to {group}")


def list_all():
    for e in load_external():
        print(f"{e['name']}  external, {e['tier']}")
    for g in sorted(p for p in PLUGINS.iterdir() if p.is_dir()):
        names = [s.name for s in skill_dirs(g)]
        print(f"{g.name} ({len(names)}){'  [ALWAYS ON]' if g.name == 'core' else ''}")
        for n in names:
            print("   ", n)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("src"); a.add_argument("--group"); a.add_argument("--always", action="store_true")
    pr = sub.add_parser("promote"); pr.add_argument("name")
    de = sub.add_parser("demote"); de.add_argument("name"); de.add_argument("--group", required=True)
    ap2 = sub.add_parser("add-plugin"); ap2.add_argument("name"); ap2.add_argument("--repo", required=True); ap2.add_argument("--path", default=""); ap2.add_argument("--tier", choices=list(TIERS), default="project"); ap2.add_argument("--desc", required=True)
    sub.add_parser("list"); sub.add_parser("build")
    x = ap.parse_args()
    if x.cmd == "add": add(x.src, x.group, x.always)
    elif x.cmd == "promote": move(x.name, "core")
    elif x.cmd == "demote": move(x.name, x.group)
    elif x.cmd == "add-plugin": add_plugin(x.name, x.repo, x.path, x.tier, x.desc)
    elif x.cmd == "list": list_all()
    elif x.cmd == "build": sys.exit(0 if build() else 1)
