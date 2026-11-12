#!/usr/bin/env python3
"""Evidence ledger: one honest record of every security or quality check, shared by all the skills.

  python3 ledger.py add --area Secrets --check "History scan" --outcome clean --proof ran --detail "8 commits, no leaks" --limit "after the fact"
  python3 ledger.py list [--area Secrets]
  python3 ledger.py summary
  python3 ledger.py validate
  python3 ledger.py export-checks report/checks.json      rows in the shape the securityreport skill draws
  python3 ledger.py markdown                              a plain table for a document

File: docs/security_ledger.json (change with --file). Vocabulary:
  outcome  clean (found nothing wrong) | fixed (found a problem, then fixed it) | open (a real finding still open) | partial (only partly proven)
  proof    ran (I ran it and saw it) | github (seen in CI records only) | both (ran and CI shows it too)
Rules the validator enforces, because they are the point of the ledger:
  * every entry has a proof: a check nobody saw run is not an entry, it is a gap (record it in gaps, not as clean)
  * every entry has a detail (what was seen) and a limit (what the check cannot tell you; write "none known" if truly none)
  * ids are unique
"""
import argparse, datetime, json, pathlib, sys

OUTCOMES = ("clean", "fixed", "open", "partial"); PROOFS = ("ran", "github", "both")


def load(path):
    p = pathlib.Path(path)
    return json.loads(p.read_text()) if p.exists() else {"checks": []}


def save(path, data):
    p = pathlib.Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")


def problems(data):
    out, seen = [], set()
    for r in data["checks"]:
        i = r.get("id")
        if i in seen: out.append(f"id {i}: duplicate")
        seen.add(i)
        if r.get("outcome") not in OUTCOMES: out.append(f"id {i}: outcome must be one of {OUTCOMES}")
        if r.get("proof") not in PROOFS: out.append(f"id {i}: proof must be one of {PROOFS} (a check nobody saw run is a gap, not an entry)")
        for k in ("area", "check", "detail", "limit"):
            if not str(r.get(k, "")).strip(): out.append(f"id {i}: {k} is empty")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default="docs/security_ledger.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for k in ("area", "check", "outcome", "proof", "detail", "limit"): a.add_argument("--" + k, required=True)
    l = sub.add_parser("list"); l.add_argument("--area")
    sub.add_parser("summary"); sub.add_parser("validate"); sub.add_parser("markdown")
    e = sub.add_parser("export-checks"); e.add_argument("out")
    x = ap.parse_args(); data = load(x.file)
    if x.cmd == "add":
        row = {"id": max([r["id"] for r in data["checks"]] + [0]) + 1, "area": x.area, "check": x.check, "outcome": x.outcome, "proof": x.proof,
               "detail": x.detail, "limit": x.limit, "date": datetime.date.today().isoformat()}
        data["checks"].append(row)
        bad = problems(data)
        if bad:
            print("NOT ADDED:", *bad, sep="\n  "); return 1
        save(x.file, data); print(f"added #{row['id']}"); return 0
    if x.cmd == "validate":
        bad = problems(data); print("\n".join(bad) if bad else f"ledger ok: {len(data['checks'])} entries"); return 1 if bad else 0
    rows = [r for r in data["checks"] if getattr(x, "area", None) in (None, r["area"])]
    if x.cmd == "list":
        for r in rows: print(f"#{r['id']:<3d} {r['area']:<18s} {r['outcome']:<8s} {r['proof']:<7s} {r['check']}")
    elif x.cmd == "summary":
        n = lambda o, rs=data["checks"]: sum(1 for r in rs if r["outcome"] == o)
        print(f"{len(data['checks'])} checks: " + ", ".join(f"{n(o)} {o}" for o in OUTCOMES))
        for area in sorted({r["area"] for r in data["checks"]}):
            rs = [r for r in data["checks"] if r["area"] == area]; print(f"  {area:<20s} " + ", ".join(f"{n(o, rs)} {o}" for o in OUTCOMES if n(o, rs)))
        att = [r for r in data["checks"] if r["outcome"] in ("open", "partial")]
        if att: print("needs attention:", *[f"  #{r['id']} {r['check']} ({r['outcome']})" for r in att], sep="\n")
    elif x.cmd == "markdown":
        print("| # | Area | Check | Outcome | Proof | What was seen | What it cannot tell you |\n|---|---|---|---|---|---|---|")
        for r in data["checks"]: print(f"| {r['id']} | {r['area']} | {r['check']} | {r['outcome']} | {r['proof']} | {r['detail']} | {r['limit']} |")
    elif x.cmd == "export-checks":
        save(x.out, [{k: r[k] for k in ("id", "area", "check", "outcome", "proof", "detail", "limit")} for r in data["checks"]]); print("wrote", x.out, len(data["checks"]), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
