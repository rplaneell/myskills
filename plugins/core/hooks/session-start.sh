#!/usr/bin/env bash
# Runs at the start of every session where the core plugin is enabled.
# 1. Prints the always on list. 2. Reminds the owner about project-template for brand new projects.
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
[ -f "$ROOT/ALWAYS.md" ] && cat "$ROOT/ALWAYS.md"
# A folder with no CLAUDE.md looks like a brand new project that skipped the template.
if [ ! -f CLAUDE.md ]; then
  echo
  echo "REMINDER FOR THE OWNER: this folder has no CLAUDE.md, so it looks like a new project."
  echo "In your first reply, tell the owner (friendly tone, no hyphens or dashes) to start new projects from the"
  echo "template repo https://github.com/rplaneell/project-template (it brings the secrets rule, the tone preferences"
  echo "and the myskills link). Offer to copy the template files into this project. Mention it only once."
fi
exit 0
