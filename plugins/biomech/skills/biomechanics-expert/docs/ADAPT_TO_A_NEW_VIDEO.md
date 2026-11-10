# Adapting the pipeline to a new video

Everything below is currently fixed inside the scripts. Change it before running on another rider.

1. **Paths.** Scripts read and write `/mnt/user-data/working` (work files) and `/home/user/ride_analysis`
   (results). `run_all.sh` creates them. Search for those two strings to move them.
2. **Rider height.** `analyse2.py`, variable `MM` (millimetres per pixel). It was calibrated as the average of
   thigh, shank, torso, upper arm and forearm length divided by the same lengths in pixels, using standard
   body proportions (thigh 0.245, shank 0.246, torso 0.288, upper arm 0.186, forearm 0.146 of height).
   For 1.735 m this gave 3.06 mm per pixel with about 8 percent error. Recompute it for a new rider.
3. **Riding styles and time ranges.** `analyse2.py`, dictionary `SEG`: one entry per steady block, with name,
   start and end in seconds. Find the blocks by plotting the torso angle against time (figure 02 does this).
   Skip warm up and transitions. Aim for 30 or more strokes per block.
4. **Which side faces the camera.** The scripts use the right side landmarks (MediaPipe indices 12, 14, 16, 24,
   26, 28, 30, 32) and assume the rider faces right. Mirror the frame or swap indices for the other side.
5. **Crank length.** Assumed 172.5 mm in the body diagram and fit schematic. Replace with the real value.
6. **Language.** All figure and report text is Catalan, spread over `pro1.py` to `pro4.py`, `metrics.py`
   (reference range names and sources) and `report.py`. Move the strings into a dictionary to translate.
7. **Rider specific text.** `pro3.py`, `pro3b.py` and `report.py` contain the rider's own numbers inside
   sentences (for example the hip angle 32 degrees and the 1.735 m height). Most are filled from the
   measured values, but a few are typed in. Search for `1,735`, `32°` and `54` before reuse.
8. **Frame size table and bike list.** `pro3.py`, figure 14. The size table is generic. The bike list is a
   general description and was not checked against manufacturer geometry tables.

## Known good settings
* MediaPipe Pose Landmarker heavy, video mode, minimum confidences 0.3.
* Butterworth low pass, second order, zero lag: 8 Hz for limbs, 4 to 5 Hz for the trunk.
* Crank phase from the geometric angle of the ball of the foot around the fitted pedal circle (0 at the top,
  90 at the front, clockwise), not from time. Strokes are cut where the phase wraps.
