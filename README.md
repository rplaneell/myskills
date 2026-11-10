# myskills

Personal marketplace of Claude Code skills and plugins. One repo, many projects.

## Connect a project (2 minutes)
1. Copy `templates/project-settings.json` into the project as `.claude/settings.json`.
2. Optionally add `templates/CLAUDE.snippet.md` to the project's `CLAUDE.md`.
3. Add extra plugins for that project by adding lines such as `"impeccable@myskills": true`. The memory plugin is `memory@myskills`.

To switch plugins on for EVERY project on your own computer, put the same JSON in `~/.claude/settings.json`.

Manual try out inside a session: `/plugin marketplace add rplaneell/myskills` then `/plugin install superpowers@myskills`.

## What is "always on"?
Three layers, from label to enforcement:
1. **Label:** every entry in `.claude-plugin/marketplace.json` starts with a tag: `[ALWAYS ON]`, `[PER PROJECT]` or `[LOCAL MACHINE ONLY]`. Source of truth: `external.json` (ready made plugins) and the `core` plugin.

3. **Enforcement:** a plugin is only really on in a project if it is `true` under `enabledPlugins` in that project's `.claude/settings.json`. The template above enables the always set.

To change the always set: edit `tier` in `external.json`, or `python3 scripts/skills.py promote NAME` / `demote NAME --group G` for skills, then update the template.

## Groups
Run `python3 scripts/skills.py list`. Enable only the groups a project needs, because every enabled skill adds its description to Claude's context.

## Add something new
- A skill folder (local or GitHub): `python3 scripts/skills.py add owner/repo/path/to/skill --group frontend`  (add `--always` to put it in core)
- A ready made plugin: `python3 scripts/skills.py add-plugin NAME --repo owner/repo --tier project --desc "..."`
- Then: `git add -A && git commit && git push`.

Skills are whole folders: `SKILL.md` plus any scripts, references and assets next to it are copied together.

## Credits (full table in NOTICE.md)
superpowers (Jesse Vincent, MIT), task-observer (Eoghan Henn, CC BY 4.0), impeccable (Paul Bakaus), claude-mem (Alex Newman, Apache 2.0), find-skills (vercel-labs/skills, MIT). Some imported skills come from third parties, keep their licences when sharing.
