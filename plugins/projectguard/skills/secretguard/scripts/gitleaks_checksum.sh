#!/usr/bin/env bash
# Print the official SHA 256 fingerprint of the gitleaks Linux download for a version, from the checksums file the gitleaks
# project publishes with each release. Usage: ./gitleaks_checksum.sh 8.30.1
# Limit: the fingerprint comes from the same release page as the download. It catches a damaged or swapped file, but it
# cannot protect you if the release itself was compromised.
set -euo pipefail
v="${1:?usage: gitleaks_checksum.sh VERSION   (for example 8.30.1)}"
curl -sSfL "https://github.com/gitleaks/gitleaks/releases/download/v${v}/gitleaks_${v}_checksums.txt" | grep "gitleaks_${v}_linux_x64.tar.gz"
