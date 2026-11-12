#!/usr/bin/env python3
"""Inventory of the inline scripts of a SHIPPED single file page against a FRESH build of the sources.

  python3 script_inventory.py shipped.html fresh_build.html [--vendor-dir src/vendor] [--min-ratio 0.5]

For every inline script in the shipped file it says one of:
  SAME      byte identical to a script of the fresh build
  CHANGED   a similar script exists in the fresh build; shows both sizes and the lines added and removed
  VENDOR    a copied in library (matches a file in --vendor-dir, or recognised by its licence header)
  MEDIA     mostly base64 data (an embedded picture, video or font), shown with its decoded size and file type
  ONLY      nothing similar in the fresh build: a feature the sources do not produce
and it lists the scripts that exist only in the fresh build.
Use it to turn "the shipped file is different" into a concrete porting list. It gives evidence, not proof: the proof is a
rebuild from sources whose fingerprint matches (see the releaseintegrity skill).
"""
import argparse, base64, difflib, hashlib, pathlib, re, sys

SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
SIGNATURES = {b"ftyp": "MP4 video", b"\x89PNG": "PNG image", b"\xff\xd8\xff": "JPEG image", b"GIF8": "GIF image", b"RIFF": "WAV or WebP", b"wOFF": "WOFF font", b"OggS": "Ogg media"}


def scripts(path):
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    return [(i, text[:m.start(1)].count("\n") + 1, m.group(1)) for i, m in enumerate(SCRIPT.finditer(text))]


def head(body):
    return re.sub(r"\s+", " ", re.sub(r"/\*+|\*+/|=+|\*", " ", body.strip()[:140])).strip()[:70]


def media_kind(body):
    s = body.strip()
    if len(s) < 5000 or len(re.findall(r"[A-Za-z0-9+/=]", s[:4000])) < 3900:
        return None
    try:
        raw = base64.b64decode(s[:80] + "=" * (-len(s[:80]) % 4))
    except Exception:
        return "base64 data"
    kind = next((v for k, v in SIGNATURES.items() if k in raw[:12]), "base64 data")
    return f"{kind}, about {len(s) * 3 / 4 / 1e6:.2f} MB decoded"


def similarity(a, b):
    return difflib.SequenceMatcher(None, a.strip()[:400], b.strip()[:400]).ratio()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shipped"); ap.add_argument("fresh")
    ap.add_argument("--vendor-dir", action="append", default=[]); ap.add_argument("--min-ratio", type=float, default=0.5)
    a = ap.parse_args()
    old, new = scripts(a.shipped), scripts(a.fresh)
    vendor = [p.read_text(encoding="utf-8", errors="replace").strip()[:300] for d in a.vendor_dir for p in sorted(pathlib.Path(d).glob("*.js"))]
    fresh_hash = {hashlib.sha1(b.strip().encode()).hexdigest(): i for i, _, b in new}
    used, rows = set(), []
    print(f"shipped: {len(old)} scripts, {sum(len(b) for _, _, b in old):,} characters   |   fresh build: {len(new)} scripts, {sum(len(b) for _, _, b in new):,} characters\n")
    for i, line, body in old:
        h = hashlib.sha1(body.strip().encode()).hexdigest()
        media = media_kind(body)
        if h in fresh_hash:
            used.add(fresh_hash[h]); tag, extra = "SAME", ""
        elif any(body.strip().startswith(v) for v in vendor) or re.search(r"@license|\bMIT License\b|Released under", body[:600]):
            tag, extra = "VENDOR", ""
        elif media:
            tag, extra = "MEDIA", media
        else:
            best = max(((similarity(body, nb), j) for j, _, nb in new), default=(0, -1))
            if best[0] >= a.min_ratio:
                j = best[1]; nb = new[j][2]; used.add(j)
                d = list(difflib.unified_diff(nb.split("\n"), body.split("\n"), lineterm="", n=0))
                add = sum(1 for l in d if l.startswith("+") and not l.startswith("+++")); rem = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
                tag, extra = "CHANGED", f"fresh #{j} has {len(nb):,} chars; shipped has {len(body):,}; +{add} / -{rem} lines"
            else:
                tag, extra = "ONLY", ""
        rows.append(tag)
        print(f"#{i:2d} line {line:6d} {len(body):10,d} chars  {tag:8s} {head(body)}" + (f"\n{'':44s}{extra}" if extra else ""))
    left = [(j, ln, b) for j, ln, b in new if j not in used]
    if left:
        print("\nscripts only in the fresh build (the shipped file lacks them):")
        for j, ln, b in left:
            print(f"#{j:2d} {len(b):10,d} chars  {head(b)}")
    print("\nsummary: " + ", ".join(f"{rows.count(t)} {t}" for t in ("SAME", "CHANGED", "VENDOR", "MEDIA", "ONLY") if rows.count(t)))


if __name__ == "__main__":
    main()
