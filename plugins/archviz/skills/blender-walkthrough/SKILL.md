---
name: blender-walkthrough
description: Render before and after 3D walkthrough videos of the loft from a JSON spec using Blender (bpy) headless. Use after the plans have been read, to check geometry with stills, and after the reform is agreed, to produce the final MP4.
---

# Blender walkthrough

Read `docs/PIPELINE.md` and `docs/WHAT_I_NEED.md` first. Run `./setup.sh` if `venv_reforma/` is missing.

## Steps
1. Fill `spec/loft_spec.json` from the plans (copy `spec/loft_spec.template.json`). Metres, real dimensions only; never invent a measurement silently. Record assumptions in the reply.
2. Geometry check: `venv_reforma/bin/python tools/build_scene.py spec/loft_spec.json --state before --stills`, then look at the PNGs and compare with the video frames. Fix the spec until it matches.
3. After the reform is agreed (`docs/REFORM_BRIEF_COUPLE.md`), add the new elements with `"states": ["after"]`, remove demolished ones from `after` with `"states": ["before"]`.
4. Camera route: eye height 1.6 m above the level z, walking speed about 1 m/s, show: entrance, main space, stairs, bed zone, bathroom.
5. Draft video (fast), then `--quality final`. Output: `renders/walkthrough_before.mp4` and `renders/walkthrough_after.mp4`.
6. Report what was assumed and what must be verified on site.

## Rules
Keep stairs within code (rise 18 cm or less) in the real spec. Without a GPU a final render is slow; use draft quality for iteration. The optional Blender MCP (`third_party/ahujasid_blender-mcp`) can be used for interactive edits.
