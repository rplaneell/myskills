---
name: reforma-planner
description: Plan the renovation of an office loft in Sant Vicenç de Castellet (Catalonia, Spain) from floor plans and a walkthrough video. Use when the user shares plans (PDF/image) or video of the loft and wants layout options, a design brief, a budget outline or an agreed reform to visualise.
---

# Reforma planner

## Inputs
Everything listed in `docs/WHAT_I_NEED.md`: floor plans, walkthrough video, measurements, photos of services, and the reason the loft is not yet habitable (ask if unknown). Brief to start from: `docs/REFORM_BRIEF_COUPLE.md` (couple, bed and new bathroom upstairs).

## Steps
1. **Read the plans.** Extract per room: name, width x length, area in m2, ceiling height, windows, doors, stairs, structural walls, wet areas (plumbing). Note the plan scale and any dimensions that are missing. Never invent a measurement: mark it "to verify on site".
2. **Read the video.** Pull key frames (`tools/extract_frames.sh`; plans with `tools/plans_to_images.py`). List current condition, materials, light, damage, services (electricity, water, heating).
3. **Brief.** Ask the user: use (living, office, mixed), occupants, budget range, style, must keep / must remove, timeline.
4. **Options.** Propose 2 to 3 layouts as a table (zones, m2, pros, cons, rough cost band). Keep structure walls unless a technician confirms otherwise.
5. **Compliance flags (not legal advice).** Remind the user to verify with a local architect or aparellador (technical architect): habitability certificate (cèdula d'habitabilitat), change of use from office to housing, municipal licence (llicència d'obres / comunicació prèvia) at the Ajuntament de Sant Vicenç de Castellet, CTE (Código Técnico de la Edificación, Spain's building code) minimums for ventilation, light, fire safety and accessibility.
6. **Agreement.** Summarise the chosen option in `design_brief.md` (rooms, dimensions, materials, furniture, lighting, camera route). Only then hand over to the `blender-walkthrough` skill, which also renders the "before" video.

## Output rules
Plain language, explain abbreviations, metric units, euros.
