#!/usr/bin/env bash
# Print the official SHA 256 fingerprint of the OSV Scanner Linux download for a release, from the project's own checksum file.
# Usage: ./osv_checksum.sh v2.7.1     (find the newest tag with: git ls-remote --tags https://github.com/google/osv-scanner)
# Limit: same release page as the download, so it catches a damaged or swapped file, not a compromised release.
set -euo pipefail
v="${1:?usage: osv_checksum.sh VERSION (for example v2.7.1)}"
curl -sSfL "https://github.com/google/osv-scanner/releases/download/${v}/osv-scanner_SHA256SUMS" | grep " osv-scanner_linux_amd64$"
