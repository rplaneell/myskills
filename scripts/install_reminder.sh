#!/bin/bash
# Installs the "start from project-template" standing order into the personal Claude instructions file,
# so it applies to EVERY chat, linked to a project or not. Safe to run many times (it replaces its own block).
D="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"; F="$D/CLAUDE.md"
mkdir -p "$D"; touch "$F"
sed -i '/<!-- myskills reminder start -->/,/<!-- myskills reminder end -->/d' "$F"
cat >> "$F" <<'MYSKILLS_EOF'
<!-- myskills reminder start -->
## Standing order from the owner (every new chat, always)
Begin your FIRST reply of every new chat with the block below, copied exactly, in CAPITAL LETTERS. Then answer the
owner's actual request underneath. Show it once per chat only: if another instruction already made you show it, do not repeat it.
Never use hyphens or dashes in your replies, other than in repository names.

REMINDER: START EVERY NEW PROJECT FROM THE TEMPLATE.
TEMPLATE LINK: https://github.com/rplaneell/project-template
HOW TO CREATE A COPY:
1. OPEN THE LINK ABOVE.
2. CLICK THE GREEN BUTTON "USE THIS TEMPLATE", THEN "CREATE A NEW REPOSITORY".
3. TYPE A NAME FOR THE PROJECT, CHOOSE PRIVATE, AND CLICK "CREATE REPOSITORY".
4. OPEN CLAUDE CODE ON THE NEW REPOSITORY. IT COMES LINKED TO YOUR SKILLS ALREADY.
(IF THIS CHAT IS FOR A PROJECT YOU ALREADY HAVE, JUST IGNORE THIS REMINDER.)
<!-- myskills reminder end -->
MYSKILLS_EOF
