"""Libraries copied into the project must be exactly the ones recorded, and the audit must know their versions.

Adapt the three marked places. Without this test an updated or swapped library would be audited at the OLD version.
"""
import hashlib, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIBS = {"examplelib": "src/vendor/examplelib.min.js"}            # 1) FILL IN: name (lowercase) -> file
HEADER = {"examplelib": r"examplelib v?(\d+\.\d+\.\d+)"}          # 2) FILL IN: regex that finds the version in the file's first 600 characters
RECORD_LINE = r"^\* (\S+) (\d+\.\d+\.\d+), .*?sha256 ([0-9a-f]{64})"   # 3) FILL IN if your THIRD_PARTY.md is written differently


def recorded():
    out = {}
    for m in re.finditer(RECORD_LINE, (ROOT / "docs/THIRD_PARTY.md").read_text(), re.M):
        out[m.group(1).lower()] = (m.group(2), m.group(3))
    return out


def test_every_vendored_library_is_recorded():
    assert set(recorded()) >= set(LIBS), recorded()


def test_vendored_files_match_their_recorded_fingerprints():
    for name, path in LIBS.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == recorded()[name][1], path


def test_the_library_headers_state_the_recorded_versions():
    for name, path in LIBS.items():
        m = re.search(HEADER[name], (ROOT / path).read_text(encoding="utf-8", errors="replace")[:600])
        assert m and m.group(1) == recorded()[name][0], (name, m and m.group(1))


def test_the_audit_list_names_the_same_versions():
    comps = {c["name"].lower(): c["version"] for c in json.loads((ROOT / "sbom/vendored.cdx.json").read_text())["components"]}
    for name in LIBS:
        assert comps.get(name) == recorded()[name][0], (name, comps.get(name))
