#!/usr/bin/env python3
"""Compare two single file web pages to learn whether one could have been built from the same sources as the other.

  python3 compare_builds.py shipped.html fresh_build.html

It prints, for each file: size, SHA 256, number of inline scripts and their total size, number of embedded data URIs
(pictures and fonts) and their total size, and the first line where the two files differ.
Reading the result: same SHA means identical. A very different script count or script size means the shipped file contains
code your sources do not produce: it was built from something else (older, newer or a different project).
This only gives evidence. The proof is rebuilding from a tagged commit and getting the same SHA.
"""
import hashlib, pathlib, re, sys


def facts(path):
    data = pathlib.Path(path).read_bytes()
    text = data.decode("utf-8", errors="replace")
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", text, re.S)
    uris = re.findall(r"data:[a-z/+.\-]+;base64,[A-Za-z0-9+/=]+", text)
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "scripts": len(scripts), "script_chars": sum(map(len, scripts)),
            "data_uris": len(uris), "data_uri_chars": sum(map(len, uris)), "lines": text.split("\n")}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a, b = facts(sys.argv[1]), facts(sys.argv[2])
    for k in ("bytes", "sha256", "scripts", "script_chars", "data_uris", "data_uri_chars"):
        flag = "" if a[k] == b[k] else "   <-- differs"
        print(f"{k:16s} {str(a[k])[:20]:>22s}  {str(b[k])[:20]:>22s}{flag}")
    for n, (x, y) in enumerate(zip(a["lines"], b["lines"]), 1):
        if x != y:
            print(f"first different line: {n}\n  A: {x[:100]}\n  B: {y[:100]}")
            break
    else:
        print("no differing line in the common part" if a["bytes"] != b["bytes"] else "files are identical")
    return 0 if a["sha256"] == b["sha256"] else 1


if __name__ == "__main__":
    sys.exit(main())
