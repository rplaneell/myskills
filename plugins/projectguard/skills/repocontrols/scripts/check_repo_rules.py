#!/usr/bin/env python3
"""Repository rules check: automatic alarms that stand in for paid branch protection.

  python3 check_repo_rules.py                 checks tracked files and workflows
  python3 check_repo_rules.py BASE..HEAD      also checks the commit messages and 'built file without source' in that range

Exit code 1 and a plain list of problems when a rule is broken. Optional settings go in .repo-rules.json at the repository root:
  {"max_bytes": 5242880,                     largest file allowed (default 5 MB)
   "big_file_ok": ["releases/", "assets/"],  folders where big files are fine
   "built_file": "dist/app.html",            a generated file that must not change without a source change (or null)
   "source_prefixes": ["src/", "build.py"],  what counts as a source change for built_file
   "subject_limit": 72,                      longest commit subject
   "extra_forbidden": ["\\\\.sqlite$"]}        more patterns for files that must never be tracked
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or ".")
DEFAULTS = {"max_bytes": 5 * 1024 * 1024, "big_file_ok": [], "built_file": None, "source_prefixes": ["src/"], "subject_limit": 72, "extra_forbidden": []}
CFG = {**DEFAULTS, **(json.loads((ROOT / ".repo-rules.json").read_text()) if (ROOT / ".repo-rules.json").exists() else {})}

FORBIDDEN = [r"(^|/)\.env($|\.(?!example$))", r"\.pem$", r"\.key$", r"(^|/)id_(rsa|dsa|ecdsa|ed25519)($|\.)",
             r"(^|/)node_modules/", r"\.p12$", r"\.pfx$"] + CFG["extra_forbidden"]
FORBIDDEN_RE = re.compile("|".join(FORBIDDEN))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def check_forbidden_files(paths):
    return [f"forbidden file is tracked by Git: {p} (secrets and dependencies must never be committed)" for p in paths if FORBIDDEN_RE.search(p)]


def check_big_files(sizes):
    return [f"file too large ({n // 1024 // 1024} MB, limit {CFG['max_bytes'] // 1024 // 1024} MB): {p}"
            for p, n in sizes.items() if n > CFG["max_bytes"] and not p.startswith(tuple(CFG["big_file_ok"]))]


def check_workflow_pins(texts):
    out = []
    for name, text in texts.items():
        for i, line in enumerate(text.split("\n"), 1):
            m = re.search(r"\buses:\s*(\S+)", line)
            if m and not m.group(1).startswith("./") and not re.search(r"@[0-9a-f]{40}$", m.group(1)):
                out.append(f"{name}:{i}: action not pinned to a full 40 character commit SHA: {m.group(1)}")
    return out


def check_message(sha, message):
    lines = message.rstrip("\n").split("\n")
    subject = lines[0].strip() if lines else ""
    out = []
    if not subject:
        out.append(f"{sha}: empty commit message")
    if len(subject) > CFG["subject_limit"]:
        out.append(f"{sha}: subject is {len(subject)} characters, limit is {CFG['subject_limit']}")
    if re.match(r"(?i)^(wip\b|fixup!|squash!|tmp\b|asdf\b|test\b)", subject):      # note: \b does not work after '!'
        out.append(f"{sha}: unfinished commit subject '{subject[:30]}' (wip, fixup, squash, tmp)")
    if len(lines) > 1 and lines[1].strip():
        out.append(f"{sha}: second line must be blank (subject, blank line, body)")
    return out


def check_built_without_source(changed):
    built = CFG["built_file"]
    if built and built in changed and not any(c.startswith(tuple(CFG["source_prefixes"])) for c in changed):
        return [f"{built} changed but no source file did (edit the sources, then rebuild)"]
    return []


def main(rng):
    problems = []
    paths = [p for p in git("ls-files").split("\n") if p]
    problems += check_forbidden_files(paths)
    problems += check_big_files({p: (ROOT / p).stat().st_size for p in paths if (ROOT / p).is_file()})
    wfdir = ROOT / ".github" / "workflows"
    wf = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in sorted(wfdir.glob("*.y*ml"))} if wfdir.exists() else {}
    problems += check_workflow_pins(wf)
    if rng:
        for sha in [s for s in git("rev-list", "--no-merges", rng).split() if s]:
            problems += check_message(sha[:7], git("log", "-1", "--format=%B", sha))
        problems += check_built_without_source(set(git("diff", "--name-only", rng).split("\n")))
    for p in problems:
        print("RULE BROKEN:", p)
    print(f"{len(problems)} problem(s). Checked {len(paths)} tracked files, {len(wf)} workflows" + (f", commits {rng}" if rng else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
