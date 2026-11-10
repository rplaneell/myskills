---
name: cycling-biomechanics
description: Analyse a side view cycling video (for example a rider on an indoor roller) into joint angles per pedal stroke, traffic light scoring against bike fit ranges with an honest error band, fit advice (saddle height, fore and aft, handlebar stack, reach), a frame size estimate and an illustrated report. Use when someone sends a cycling video and asks for pedalling form, bike fit or position analysis.
---

# Cycling biomechanics from one side view video

## When to use
A person shares a video of themselves cycling from the side and wants their pedalling form and position
analysed, with images first and text only to explain them. Keep the tone friendly, explain every abbreviation the
first time it appears, and write in the language they ask for (the first run was in Catalan). Never use hyphens or
dashes in prose if the user has asked for that.

## Ground rules
* Never invent results. If a tool cannot run, say which one and why, and give the exact commands to run elsewhere.
* Secrets: keys and tokens only in a local `.env`, with `.env` in `.gitignore` before the first commit, and a
  `.env.example` with empty values. The tools here need no API keys.
* Videos and images show a person. Keep them out of git. Create repos private.
* Put every number next to its error. Do not draw conclusions from differences smaller than the error.
* Reference ranges are rules of thumb. Say so, and cite the reasoning (see `docs/REFERENCE_RANGES.md`).

## Method (the order the pipeline runs)
1. **Check the video.** Frame rate, resolution, length, camera side. Handheld, low resolution and 30 fps all add
   error. Draw the skeleton on a start, middle and end frame and look at them before trusting anything.
2. **Split the video into riding styles.** Plot the torso angle against time. Riders often change hand position
   or stand up. Analyse each steady block separately and skip transitions.
3. **Track.** MediaPipe Pose Landmarker (heavy) in video mode. Only the side facing the camera is reliable; the
   far leg is guessed by the model, so do not score left versus right from one camera.
4. **Smooth and phase.** Low pass filter, then compute the crank angle geometrically (angle of the ball of the
   foot around the fitted pedal circle, 0 at the top, clockwise) and cut strokes where the phase wraps.
5. **Measure per stroke.** Knee extension and minimum, hip angle at the top, torso, elbow, shoulder, ankle range,
   cadence and its spread, pelvis bounce, knee against the ball of the foot at 3 o'clock, stroke to stroke spread.
6. **Calibrate scale from the rider's height** using standard segment proportions. Millimetres then carry about
   8 percent error. Angles do not need the scale.
7. **Traffic lights and score** with simulated error, then **fit advice** with conversions in millimetres.
8. **Figures** in one design system (one typeface, thin lines, a plate with title and two caption blocks), then
   the **report** as a scrollable page and a PDF.
9. **Retest plan**: camera at bottom bracket height, level, about 3 m away, drive side, 60 fps, markers on hip,
   knee, ankle and ball of the foot, 2 to 3 minutes per style, plus a clip after a hard session.

## Lessons learned (save the next session time)
* Sports2D (RTMPose) installs by pip, but its models download from `download.openmmlab.com` and
  `huggingface.co`. If the network blocks them (403), say so plainly. Option names changed: newer versions use
  `--nb_persons_to_detect 1` and `--visible_side right` instead of `--multiperson false`.
* MediaPipe on a bare Linux box needs `libegl1` and `libgles2`. A traceback at interpreter shutdown after the
  data file is saved is harmless.
* OpenCV frame seeking was exact on this file. If skeleton and image disagree, check you passed the frame index
  to the drawing function (a swapped argument looked exactly like a tracking failure).
* The pedal circle fit alone gave a poor scale; calibrating from body proportions and height was better.
* Hand held video drifts, so use angles and positions relative to the bike or the hip, not absolute pixels.
* Short clips give few strokes. With under about 10 strokes per block, label confidence low.
* The hip landmark is a joint centre estimate. Markers on the body reduce this error.
* Do not recommend a frame size or a bike model as final without the rider's inseam and their current bike
  geometry. Say that manufacturer tables were not verified if they were not.
* Fix one thing at a time. The first fixes in the first session were the handlebar height for a closed hip
  angle, soft elbows, and a small saddle drop only if pelvis bounce persisted.
* Flag when to see a physio or a professional bike fitter: pain at the front of the hip or lower back, tingling in
  the hands, knee pain, a feeling that one leg works less.

## Files
`pipeline/` holds the scripts and `pipeline/run_all.sh` gives the order. `docs/ADAPT_TO_A_NEW_VIDEO.md` lists
what is still fixed inside them. The first thing to do in a new session is to generalise those settings.
