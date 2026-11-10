---
name: archviz-walkthrough
description: Direct and render cinematic architectural walk through videos from floor plans and measurements (camera clearance, eye level, independent look at target, spline arcs, constant speed, no dead stops, short tracking shots, stabilization). Use when planning camera routes or rendering walk through videos of the loft, or any interior, with tools/director.py.
---

# Architectural visualization walk through

Owner supplied principles, kept verbatim in `docs/ARCHVIZ_PRINCIPLES.md`. This skill turns them into the workflow of this repository.

## Rules (from the principles)
1. **Clearance:** keep the camera 0.8 to 1.0 m from walls, glass and railings. Check every frame with `tools/check_clearance.py` and fix the route when a shot drops below that. Where a room is physically narrower (accessible bathroom 1.28 m, hall 1.56 m, stair 0.93 m), keep the camera on the centre line and say so.
2. **Eye level:** 1.50 to 1.65 m above the current floor (ground floor, stair tread or mezzanine).
3. **Independent target:** camera path and look at target are separate splines; the target pans towards the next focal point before the camera reaches the turn.
4. **Sloped ceilings:** route through the tallest zone (upstairs: x of 3.9 m or more, next to the back wall); never tilt up towards the ceiling.
5. **Corners:** smooth spline arcs only (centripetal Catmull Rom in `tools/director.py`), no linear corners.
6. **Speed:** constant inside a shot, about 1.2 m/s; frame count = path length / speed x 24. Slower constant speeds are allowed only in the tiny rooms and under the slope, and must be documented.
7. **No dead stops:** never a frame with zero velocity; no dwell.
8. **Easing:** ease in and out only on the panning (yaw and pitch).
9. **Multi shot:** 4 to 8 s tracking shots joined by cuts; cut away before any collision or hesitation.
10. **Stabilization:** Gaussian smoothing of yaw and pitch (and optionally ffmpeg vidstab on the final sequence).
11. **Real frames:** render every frame at 24 fps. Do not fabricate in between frames by interpolation; it shows as trembling on thin railings.

## Workflow
1. Geometry from the plans: `tools/real_loft.py` (measured from the DWG, assumptions in `docs/REAL_LOFT_NOTES.md`).
2. Shots: edit `SHOTS` in `tools/director.py`, then `python tools/director.py` to list durations.
3. Clearance: `python tools/check_clearance.py`.
4. Render: `python tools/render_walk.py --state after --director --out renders/proposal_v2`.
5. Assemble: `python tools/make_director_video.py` (cuts, captions, grade).

## Tool stack named in the principles
IfcOpenShell (BIM data, when an IFC exists), Blender bpy (used here), ComfyUI with AnimateDiff and 3D Gaussian Splatting (both need a GPU; not available in this environment).
