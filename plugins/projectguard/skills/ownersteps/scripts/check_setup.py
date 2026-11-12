#!/usr/bin/env python3
"""Check, ON THE OWNER'S COMPUTER, that the local protections are really switched on. Works on Windows, macOS and Linux.

  python check_setup.py            run it inside the project folder

It reports DONE or NOT DONE for each item, with the exact fix in plain words. Exit code 0 only if everything is DONE.
Why it exists: an assistant working in a cloud container cannot install anything on the owner's computer, and a hook that was
never installed protects nothing. This turns "I think it is installed" into a fact.
"""
import os, pathlib, shutil, subprocess, sys


def run(*cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, ""


def main():
    results = []
    def item(ok, name, fix):
        results.append(ok); print(("DONE      " if ok else "NOT DONE  ") + name)
        if not ok: print("          fix: " + fix)

    code, top = run("git", "rev-parse", "--show-toplevel")
    if code != 0:
        print("This is not a Git project folder. Open a terminal inside the project and run this again."); return 1
    root = pathlib.Path(top); os.chdir(root)
    print(f"Project: {root}\n")
    item(shutil.which("pre-commit") is not None or run(sys.executable, "-m", "pre_commit", "--version")[0] == 0,
         "the pre-commit program is installed", "run:  pip install pre-commit      (on Windows you may need:  py -m pip install pre-commit)")
    item((root / ".pre-commit-config.yaml").is_file(), "the project has a .pre-commit-config.yaml", "ask for the file to be added to the project (it lists the secret scanner)")
    hooks = root / ".git" / "hooks"
    for name, what in (("pre-commit", "commit blocker (refuses a commit that contains a key)"), ("pre-push", "push blocker (refuses a direct push to main)")):
        f = hooks / name
        item(f.is_file() and "pre-commit" in f.read_text(errors="replace"), f"the {what} is switched on", "run once inside the project:  pre-commit install")
    ignored = run("git", "check-ignore", "-q", ".env")[0] == 0
    item(ignored, "a file called .env is ignored by Git", "add the line  .env  to the file .gitignore")
    item(run("git", "ls-files", "--error-unmatch", ".env")[0] != 0, "no .env file is tracked by Git", "run:  git rm --cached .env   then commit, and revoke any key that was in it")
    name = run("git", "config", "user.name")[1]; email = run("git", "config", "user.email")[1]
    item(bool(name and email), f"Git knows who you are ({name or '?'})", 'run:  git config user.name "Your Name"   and   git config user.email "you@example.com"')
    print()
    if all(results):
        print("Everything is switched on. Test the blocker once with a made up key: see the secretguard skill (test_blocker.sh).")
        return 0
    print("Fix the NOT DONE lines, then run this again. Nothing was changed by this check.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
