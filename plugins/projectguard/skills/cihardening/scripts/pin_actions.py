#!/usr/bin/env python3
"""Pin every GitHub Action to a full commit SHA and keep the version as a comment.

Why: a version tag such as v4 can be moved to different code at any time (by a mistake or by an attacker who
took over the action's repository). A full commit SHA (a 40 character fingerprint of the code) cannot move.

  python3 pin_actions.py                 check only: lists unpinned actions, exit code 1 if any (changes nothing)
  python3 pin_actions.py --write         resolve each tag to its commit and rewrite the workflow files
  python3 pin_actions.py --write --newest   a moving major tag such as v4 is pinned to the NEWEST v4.x.y release

Options: --workflows DIR (default .github/workflows)
Needs: git and internet access (it asks GitHub with `git ls-remote`, nothing is downloaded).
Limits: it cannot tell if the code behind a tag was already bad before you pinned it. Pinning protects against FUTURE changes.
"""
import argparse, datetime, pathlib, re, subprocess, sys

USES = re.compile(r"^(?P<head>\s*-?\s*uses:\s*)(?P<action>[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@(?P<ref>[^\s#]+)(?P<tail>\s*#.*)?\s*$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def ls_remote(repo, pattern):
    out = subprocess.run(["git", "ls-remote", f"https://github.com/{repo}", pattern], capture_output=True, text=True)
    return [ln.split("\t") for ln in out.stdout.strip().splitlines() if "\t" in ln]


def resolve_tag(repo, tag):
    """Commit SHA a tag points to. Annotated tags have a peeled line (^{}) holding the real commit."""
    found = {}
    for sha, ref in ls_remote(repo, f"refs/tags/{tag}*"):
        name = ref[len("refs/tags/"):]
        if name == tag or name == tag + "^{}":
            found[name] = sha
    return found.get(tag + "^{}") or found.get(tag)


def newest_in_major(repo, major):
    best = None
    for sha, ref in ls_remote(repo, f"refs/tags/v{major}.*"):
        name = ref[len("refs/tags/"):].removesuffix("^{}")
        m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", name)
        if m:
            key = tuple(map(int, m.groups()))
            if best is None or key > best[0]:
                best = (key, name)
    return best[1] if best else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workflows", default=".github/workflows")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--newest", action="store_true", help="pin a bare major tag (v4) to the newest vMAJOR.x.y release")
    a = ap.parse_args()
    files = sorted(pathlib.Path(a.workflows).glob("*.y*ml"))
    if not files:
        sys.exit(f"no workflow files in {a.workflows}")
    problems = 0
    for f in files:
        lines, changed = f.read_text(encoding="utf-8").split("\n"), False
        for i, line in enumerate(lines):
            m = USES.match(line)
            if not m or m["action"].startswith("./") or SHA.match(m["ref"]):
                continue
            problems += 1
            repo = "/".join(m["action"].split("/")[:2])
            print(f"{f}:{i + 1}: not pinned: {m['action']}@{m['ref']}")
            if not a.write:
                continue
            tag = m["ref"]
            if a.newest and re.fullmatch(r"v?\d+", tag):
                tag = newest_in_major(repo, tag.lstrip("v")) or tag
            sha = resolve_tag(repo, tag)
            if not sha:
                print(f"    could not resolve {repo}@{tag}; left unchanged", file=sys.stderr)
                continue
            lines[i] = f"{m['head']}{m['action']}@{sha} # {tag}"
            changed = True
            print(f"    pinned to {sha[:12]}... # {tag}")
        if changed:
            f.write_text("\n".join(lines), encoding="utf-8")
    if problems and not a.write:
        print(f"\n{problems} action(s) not pinned. Run with --write to fix.")
        return 1
    print("all actions are pinned" if not problems else f"\n{problems} action(s) handled ({datetime.date.today()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
