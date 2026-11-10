#!/usr/bin/env bash
# Runs at the start of every NEW chat where the core plugin is enabled.
# 1. Prints the always on list. 2. Orders Claude to open its first reply with the project template reminder.
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
[ -f "$ROOT/ALWAYS.md" ] && cat "$ROOT/ALWAYS.md"
cat <<'MSG'

STANDING ORDER FROM THE OWNER (applies to every new chat, always):
Begin your FIRST reply of this chat with the block below, copied exactly, in CAPITAL LETTERS, then answer the
owner's actual request normally underneath. Show it only in the first reply of the chat. Do not use hyphens or dashes
in anything you write, other than the repository name itself.

REMINDER: START EVERY NEW PROJECT FROM THE TEMPLATE.
TEMPLATE LINK: https://github.com/rplaneell/project-template
HOW TO CREATE A COPY:
1. OPEN THE LINK ABOVE.
2. CLICK THE GREEN BUTTON "USE THIS TEMPLATE", THEN "CREATE A NEW REPOSITORY".
3. TYPE A NAME FOR THE PROJECT, CHOOSE PRIVATE, AND CLICK "CREATE REPOSITORY".
4. OPEN CLAUDE CODE ON THE NEW REPOSITORY. IT COMES LINKED TO YOUR SKILLS ALREADY.
(IF THIS CHAT IS FOR A PROJECT YOU ALREADY HAVE, JUST IGNORE THIS REMINDER.)
MSG
exit 0
